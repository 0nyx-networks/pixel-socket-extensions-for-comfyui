from comfy_api.latest import ComfyExtension, io as comfy_api_io # pyright: ignore[reportMissingImports]

class PixelSocketExtensions(ComfyExtension):
    async def get_node_list(self) -> list[type[comfy_api_io.ComfyNode]]:
        from .pixel_socket_node_delivery import PixelSocketDeliveryImageNode
        from .pixel_socket_node_load import PixelSocketLoadImageFromUrlNode
        from .pixel_socket_node_resize import PixelSocketResizeImageNode

        return [
                    PixelSocketDeliveryImageNode,
                    PixelSocketLoadImageFromUrlNode,
                    PixelSocketResizeImageNode,
               ]

async def comfy_entrypoint() -> ComfyExtension:
    return PixelSocketExtensions()
