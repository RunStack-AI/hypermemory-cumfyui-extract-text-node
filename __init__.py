from .nodes import HyperMemoryExtractText, comfy_entrypoint

NODE_CLASS_MAPPINGS = {
    "HyperMemoryExtractText": HyperMemoryExtractText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HyperMemoryExtractText": "HyperMemory Extract Text",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "comfy_entrypoint"]
