from comfy_api.latest import ComfyExtension, io

from .core import (
    extract_text,
    generate_hypermemory_text,
)


class HyperMemoryExtractText(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="HyperMemoryExtractText",
            search_aliases=[
                "extract text",
                "regex extract",
                "hypermemory",
                "brand prompt",
                "openrouter",
            ],
            display_name="Extract Text - Hypermemory",
            category="text/HyperMemory",
            description=(
                "Extract text using ComfyUI's regex Extract Text behavior, recall "
                "brand context from HyperMemory, and generate an on-brand prompt "
                "through OpenRouter."
            ),
            inputs=[
                io.String.Input("string", multiline=True),
                io.String.Input("regex_pattern", multiline=True),
                io.Combo.Input(
                    "mode",
                    options=["First Group", "First Match", "All Matches", "All Groups"],
                ),
                io.Boolean.Input("case_insensitive", default=True, advanced=True),
                io.Boolean.Input("multiline", default=False, advanced=True),
                io.Boolean.Input("dotall", default=False, advanced=True),
                io.Int.Input("group_index", default=1, min=0, max=100, advanced=True),
            ],
            outputs=[
                io.String.Output(),
            ],
        )

    @classmethod
    def execute(
        cls,
        string,
        regex_pattern,
        mode,
        case_insensitive=True,
        multiline=False,
        dotall=False,
        group_index=1,
    ):
        extracted_text = extract_text(
            string,
            regex_pattern,
            mode,
            case_insensitive=case_insensitive,
            multiline=multiline,
            dotall=dotall,
            group_index=group_index,
        )

        return io.NodeOutput(generate_hypermemory_text(extracted_text))


class HyperMemoryExtractTextExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [HyperMemoryExtractText]


async def comfy_entrypoint() -> HyperMemoryExtractTextExtension:
    return HyperMemoryExtractTextExtension()
