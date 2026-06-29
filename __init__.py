from .nodes import HyperMemoryExtractText, comfy_entrypoint

NODE_CLASS_MAPPINGS = {
    "HyperMemoryExtractText": HyperMemoryExtractText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HyperMemoryExtractText": "Extract Text - Hypermemory",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "comfy_entrypoint"]
