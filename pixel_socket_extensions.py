from comfy_api.latest import ComfyExtension, io as comfy_api_io # pyright: ignore[reportMissingImports]

class PixelSocketExtensions(ComfyExtension):
    async def get_node_list(self) -> list[type[comfy_api_io.ComfyNode]]:
        from .pixel_socket_node_delivery import PixelSocketDeliveryImageNode
        from .pixel_socket_node_load_url import PixelSocketLoadImageFromUrlNode
        from .pixel_socket_node_resize import PixelSocketResizeImageNode
        from .pixel_socket_node_load_pnginfo import PixelSocketLoadImageInfoNode
        return [
                    PixelSocketDeliveryImageNode,
                    PixelSocketLoadImageFromUrlNode,
                    PixelSocketResizeImageNode,
                    PixelSocketLoadImageInfoNode,
               ]

async def comfy_entrypoint() -> ComfyExtension:
    return PixelSocketExtensions()
