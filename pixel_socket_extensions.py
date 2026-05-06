from comfy_api.latest import ComfyExtension, io as comfy_api_io # pyright: ignore[reportMissingImports]

from pixel_socket_delivery_image import PixelSocketDeliveryImageNode
from pixel_socket_delivery_video import PixelSocketDeliveryVideoNode

class PixelSocketExtensions(ComfyExtension):
    async def get_node_list(self) -> list[type[comfy_api_io.ComfyNode]]:
        return [
                    PixelSocketDeliveryImageNode,
                    PixelSocketDeliveryVideoNode,
               ]

async def comfy_entrypoint() -> ComfyExtension:
    return PixelSocketExtensions()
