from comfy_api.latest import ComfyExtension, io

from .core import (
    DEFAULT_HYPERMEMORY_API_URL,
    DEFAULT_OPENROUTER_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    HyperMemoryError,
    OpenRouterError,
    assemble_prompt,
    call_openrouter,
    extract_text,
    format_hypermemory_context,
    recall_hypermemory,
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
            display_name="HyperMemory Extract Text",
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
                    options=["First Match", "All Matches", "First Group", "All Groups"],
                ),
                io.String.Input("hypermemory_api_key", default=""),
                io.String.Input("openrouter_api_key", default=""),
                io.String.Input("brand_details", multiline=True, default=""),
                io.String.Input("hypermemory_query", multiline=True, default="", advanced=True),
                io.String.Input(
                    "hypermemory_api_url",
                    default=DEFAULT_HYPERMEMORY_API_URL,
                    advanced=True,
                ),
                io.Int.Input("max_results", default=10, min=1, max=50, advanced=True),
                io.Boolean.Input("use_hypermemory", default=True, advanced=True),
                io.String.Input(
                    "openrouter_model",
                    default=DEFAULT_OPENROUTER_MODEL,
                    advanced=True,
                ),
                io.String.Input(
                    "system_prompt",
                    multiline=True,
                    default=DEFAULT_SYSTEM_PROMPT,
                    advanced=True,
                ),
                io.Float.Input(
                    "temperature",
                    default=0.4,
                    min=0.0,
                    max=2.0,
                    step=0.05,
                    advanced=True,
                ),
                io.Int.Input(
                    "max_tokens",
                    default=900,
                    min=64,
                    max=8192,
                    step=64,
                    advanced=True,
                ),
                io.Boolean.Input("generate_with_openrouter", default=True, advanced=True),
                io.Boolean.Input("case_insensitive", default=True, advanced=True),
                io.Boolean.Input("multiline", default=False, advanced=True),
                io.Boolean.Input("dotall", default=False, advanced=True),
                io.Int.Input("group_index", default=1, min=0, max=100, advanced=True),
            ],
            outputs=[
                io.String.Output(display_name="extracted_text"),
                io.String.Output(display_name="memory_context"),
                io.String.Output(display_name="assembled_prompt"),
                io.String.Output(display_name="llm_output"),
                io.String.Output(display_name="status"),
            ],
        )

    @classmethod
    def execute(
        cls,
        string,
        regex_pattern,
        mode,
        hypermemory_api_key,
        openrouter_api_key,
        brand_details,
        hypermemory_query="",
        hypermemory_api_url=DEFAULT_HYPERMEMORY_API_URL,
        max_results=10,
        use_hypermemory=True,
        openrouter_model=DEFAULT_OPENROUTER_MODEL,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        temperature=0.4,
        max_tokens=900,
        generate_with_openrouter=True,
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

        statuses = []
        memory_context = ""
        query = (hypermemory_query or extracted_text).strip()

        if use_hypermemory:
            if not hypermemory_api_key.strip():
                statuses.append("HyperMemory skipped: API key is missing.")
            elif not query:
                statuses.append("HyperMemory skipped: query is empty.")
            else:
                try:
                    memory_response = recall_hypermemory(
                        hypermemory_api_key,
                        hypermemory_api_url,
                        query,
                        max_results=max_results,
                    )
                    memory_context = format_hypermemory_context(memory_response)
                    statuses.append("HyperMemory recall completed.")
                except HyperMemoryError as exc:
                    statuses.append(str(exc))
        else:
            statuses.append("HyperMemory disabled.")

        assembled_prompt = assemble_prompt(extracted_text, brand_details, memory_context)

        if generate_with_openrouter:
            if not openrouter_api_key.strip():
                llm_output = "OpenRouter API key is required when generation is enabled."
                statuses.append("OpenRouter skipped: API key is missing.")
            else:
                try:
                    llm_output = call_openrouter(
                        openrouter_api_key,
                        openrouter_model,
                        system_prompt,
                        assembled_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    statuses.append("OpenRouter generation completed.")
                except OpenRouterError as exc:
                    llm_output = str(exc)
                    statuses.append(f"OpenRouter error: {exc}")
        else:
            llm_output = assembled_prompt
            statuses.append("OpenRouter generation disabled.")

        return io.NodeOutput(
            extracted_text,
            memory_context,
            assembled_prompt,
            llm_output,
            " ".join(statuses).strip(),
        )


class HyperMemoryExtractTextExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [HyperMemoryExtractText]


async def comfy_entrypoint() -> HyperMemoryExtractTextExtension:
    return HyperMemoryExtractTextExtension()
