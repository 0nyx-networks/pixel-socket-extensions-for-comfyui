import json
from typing import Any

from PIL import Image
import piexif
from comfy_api.latest import io as comfy_api_io, ui as comfy_api_ui # pyright: ignore[reportMissingImports]
import torch # pyright: ignore[reportMissingImports]

class PixelSocketLoadImageInfoNode(comfy_api_io.ComfyNode):
    @classmethod
    def define_schema(cls) -> comfy_api_io.Schema:
        return comfy_api_io.Schema(
            node_id="PixelSocketLoadImageInfo",
            display_name="Load Image info",
            category="PixelSocket/Load",
            is_output_node=True,
            inputs=[
                comfy_api_io.Combo.Input("image",
                    upload=comfy_api_io.UploadType.image
                )
            ],
            outputs=[
                comfy_api_io.String.Output("positive_prompt"),
                comfy_api_io.String.Output("negative_prompt"),
                comfy_api_io.String.Output("metadata"),
            ]
        )

    @classmethod
    def execute(cls, image: Image.Image, **kwargs) -> Any:
        def parse_geninfo(geninfo: str):
            """
            geninfo テキストをパースして positive_prompt, negative_prompt, メタデータを抽出
            <lora:...> 形式のテキストを除外
            """
            import re

            # "Negative prompt:" で分割
            if "Negative prompt:" in geninfo:
                parts = geninfo.split("Negative prompt:", 1)
                positive_prompt = parts[0].strip()

                negative_part = parts[1]

                # メタデータの開始位置を検出（最初のメタデータキーを探す）
                # メタデータキーは "キー名: 値" の形式で、通常キー名は複数単語
                metadata_match = re.search(r'\s\w+\s*:', negative_part)

                if metadata_match:
                    # メタデータの開始位置
                    metadata_start = metadata_match.start()
                    negative_prompt = negative_part[:metadata_start].strip()
                    metadata_text = negative_part[metadata_start:]
                else:
                    # メタデータが見つからない場合は全て negative_prompt
                    negative_prompt = negative_part.strip()
                    metadata_text = ""
            else:
                # "Negative prompt:" がない場合は全体が positive_prompt
                positive_prompt = geninfo.strip()
                negative_prompt = ""
                metadata_text = ""

            # <lora:...> 形式のテキストを除外
            positive_prompt = re.sub(r'<lora:[^>]+>\s*', '', positive_prompt)
            negative_prompt = re.sub(r'<lora:[^>]+>\s*', '', negative_prompt)

            # メタデータを抽出
            metadata = {}
            if metadata_text:
                # "key: value" 形式で分割
                # ただしクォートで囲まれた値や複雑な値に対応
                pairs = re.findall(r'(\w+(?:\s+\w+)*?)\s*:\s*([^,]+?)(?=,\s*\w+\s*:|$)', metadata_text)
                for key, value in pairs:
                    key = key.strip()
                    value = value.strip().strip('"')
                    metadata[key] = value

            return positive_prompt.strip(), negative_prompt.strip(), json.dumps(metadata)

        items = (image.info or {}).copy()

        geninfo: str = items.pop('parameters', None)


        if "exif" in items:
            exif_data = items["exif"]
            try:
                exif = piexif.load(exif_data)
            except OSError:
                # memory / exif was not valid so piexif tried to read from a file
                exif = None
            exif_comment = (exif or {}).get("Exif", {}).get(piexif.ExifIFD.UserComment, b'')
            try:
                exif_comment = piexif.helper.UserComment.load(exif_comment) # type: ignore
            except ValueError:
                exif_comment = exif_comment.decode('utf8', errors="ignore")

            if exif_comment:
                geninfo = exif_comment

        elif "comment" in items: # for gif
            if isinstance(items["comment"], bytes):
                geninfo = items["comment"].decode('utf8', errors="ignore")
            else:
                geninfo = items["comment"]

        if items.get("Software", None) == "NovelAI":
            pass

        # geninfo をパース
        (positive_prompt, negative_prompt, metadata) = parse_geninfo(geninfo or "")

        # デバッグ/確認用に出力
        print(f"[PixelSocketLoadPNGinfoFromImage] Positive Prompt: {positive_prompt[:100]}...")
        print(f"[PixelSocketLoadPNGinfoFromImage] Negative Prompt: {negative_prompt[:100]}...")
        print(f"[PixelSocketLoadPNGinfoFromImage] Metadata: {metadata}")

        return comfy_api_io.NodeOutput(positive_prompt, negative_prompt, metadata, ui=comfy_api_ui.PreviewImage(image, cls=cls))
