# HyperMemory ComfyUI Extract Text Node

Turn rough text into on-brand generation prompts inside ComfyUI.

This custom node starts from ComfyUI's familiar `Extract Text` regex behavior, then adds brand memory recall from HyperMemory and prompt refinement through OpenRouter. It is built for marketing, product, and creative workflows where every generated image or video should remember the brand.

![ComfyUI](https://img.shields.io/badge/ComfyUI-custom_node-111111)
![HyperMemory](https://img.shields.io/badge/HyperMemory-brand_context-4f46e5)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM_prompts-10b981)
![Python](https://img.shields.io/badge/Python-stdlib_only-3776ab)
![License](https://img.shields.io/badge/License-MIT-f59e0b)

## What It Does

`HyperMemory Extract Text` is a single ComfyUI node that:

1. Extracts useful text with the same regex modes as ComfyUI's built-in `Extract Text` node.
2. Uses the extracted text, or a custom query, to recall brand context from HyperMemory.
3. Combines the extracted text, explicit brand details, and remembered context into a structured prompt.
4. Sends that prompt to OpenRouter and returns a polished final prompt for image or video generation.

The default OpenRouter model is `minimax/minimax-m3`.

## Install

Clone this repo into your ComfyUI custom nodes folder:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RunStack-AI/hypermemory-cumfyui-extract-text-node.git
```

Restart ComfyUI. The node appears as:

```text
text/HyperMemory -> HyperMemory Extract Text
```

No extra Python packages are required.

## How To Use

### 1. Add The Node

In ComfyUI, right-click the canvas and add:

```text
text/HyperMemory -> HyperMemory Extract Text
```

The node is meant to sit between your rough text input and your final prompt consumer, such as CLIP Text Encode, an image generation node, or a video generation node.

### 2. Connect Source Text

Send any rough brief, caption, transcript, product note, or campaign instruction into `string`.

You can paste text directly into the node, or wire text from another node. The node will run regex extraction first, before it talks to HyperMemory or OpenRouter.

Example source text:

```text
Campaign brief: 15 second teaser for the new running shoe line.
Focus on speed, city lights, and premium performance.
```

### 3. Choose What To Extract

Set `regex_pattern` and `mode` just like ComfyUI's built-in `Extract Text` node.

Example regex:

```regex
Campaign brief:\s*(.*)
```

Recommended mode for the example above:

```text
First Group
```

That extracts:

```text
15 second teaser for the new running shoe line.
```

Common extraction patterns:

| Goal | Regex | Mode |
|---|---|---|
| Extract everything after a label | `Brief:\s*(.*)` | `First Group` |
| Extract every hashtag | `#(\w+)` | `All Groups` |
| Extract the first quoted phrase | `"([^"]+)"` | `First Group` |
| Extract the first URL | `https?://\S+` | `First Match` |
| Extract all numbered lines | `^\d+\.\s*(.*)` | `All Groups` with `multiline` on |

If the regex does not match, `extracted_text` is empty. The node will still return a useful `status` message so you can debug the pattern.

### 4. Add Brand Details

Use `brand_details` for the things you always want the prompt to respect: voice, audience, colors, visual rules, product constraints, and anything the model should avoid.

Example brand details:

```text
Premium athletic brand. Energetic but refined. Avoid hypebeast slang.
Use night city visuals, sharp contrast, clean product framing, and electric blue accents.
```

This explicit text is combined with whatever HyperMemory recalls, so you can use it for immediate direction even before the brand graph is fully populated.

### 5. Connect HyperMemory

Paste a HyperMemory API key into `hypermemory_api_key`.

Leave `hypermemory_query` blank if you want the node to search memory using `extracted_text`. Use `hypermemory_query` when you want a more targeted lookup, for example:

```text
brand voice visual style sneaker launch campaign
```

Useful settings:

| Setting | Recommended Start |
|---|---|
| `use_hypermemory` | `true` |
| `hypermemory_api_url` | `https://api.hypermemory.io` |
| `max_results` | `5` to `10` |

The `memory_context` output shows exactly what came back from HyperMemory. If the context is too broad, make `hypermemory_query` more specific. If it is too thin, increase `max_results` or store more brand context in HyperMemory.

### 6. Connect OpenRouter

Paste an OpenRouter API key into `openrouter_api_key`.

The default model is:

```text
minimax/minimax-m3
```

You can swap `openrouter_model` for any OpenRouter model slug you prefer. Keep `temperature` around `0.3` to `0.6` for controlled brand prompt writing, and raise it only when you want more exploratory creative language.

If you turn `generate_with_openrouter` off, the node skips the LLM call and returns `assembled_prompt` as `llm_output`. This is useful when you want to inspect the exact prompt before spending OpenRouter credits.

### 7. Wire The Outputs

Use the output that matches your workflow:

| Output | Best Use |
|---|---|
| `extracted_text` | Debug the regex extraction. |
| `memory_context` | Inspect what HyperMemory remembered. |
| `assembled_prompt` | Review the full prompt before the LLM rewrite. |
| `llm_output` | Send to CLIP Text Encode, image generation, or video generation. |
| `status` | Debug missing keys, empty regex matches, or provider errors. |

Typical production wiring:

```text
HyperMemory Extract Text.llm_output -> CLIP Text Encode.text
```

Typical debugging wiring:

```text
HyperMemory Extract Text.extracted_text
HyperMemory Extract Text.memory_context
HyperMemory Extract Text.assembled_prompt
HyperMemory Extract Text.status
```

### 8. A Complete Mini Example

Input:

```text
Campaign brief: 15 second teaser for the new running shoe line.
Focus on speed, city lights, and premium performance.
```

Regex:

```regex
Campaign brief:\s*(.*)
```

Mode:

```text
First Group
```

HyperMemory query:

```text
running shoe campaign brand guidelines city lights performance
```

Downstream:

```text
llm_output -> CLIP Text Encode -> video generation
```

## Inputs

| Input | Purpose |
|---|---|
| `string` | Source text to extract from. |
| `regex_pattern` | Regex pattern used by the Extract Text behavior. |
| `mode` | `First Match`, `All Matches`, `First Group`, or `All Groups`. |
| `hypermemory_api_key` | HyperMemory `hm_...` API key. |
| `openrouter_api_key` | OpenRouter API key. |
| `brand_details` | Explicit brand voice, audience, product, and visual guidance. |
| `hypermemory_query` | Optional recall query. If blank, the node uses `extracted_text`. |
| `hypermemory_api_url` | Defaults to `https://api.hypermemory.io`. |
| `max_results` | Number of HyperMemory recall results, default `10`. |
| `use_hypermemory` | Turn memory recall on or off. |
| `openrouter_model` | Defaults to `minimax/minimax-m3`. |
| `system_prompt` | Instruction for the OpenRouter model. |
| `temperature` | Generation temperature, default `0.4`. |
| `max_tokens` | OpenRouter response budget, default `900`. |
| `generate_with_openrouter` | Turn OpenRouter generation on or off. |

Advanced regex controls are also included: `case_insensitive`, `multiline`, `dotall`, and `group_index`.

## Outputs

| Output | Meaning |
|---|---|
| `extracted_text` | The regex extraction result. |
| `memory_context` | Formatted HyperMemory recall results. |
| `assembled_prompt` | The complete prompt sent to OpenRouter. |
| `llm_output` | The final on-brand prompt, or setup/error text. |
| `status` | A short execution summary. |

## Workflow Pattern

```text
Source Text
   |
   v
HyperMemory Extract Text
   |-- extracted_text
   |-- memory_context
   |-- assembled_prompt
   v
llm_output
   |
   v
CLIP Text Encode / Image Generation / Video Generation
```

For prompt debugging, inspect `assembled_prompt` first. For production generation, wire `llm_output` downstream.

## API Keys And Graphs

The node accepts API keys directly as inputs because that is convenient in ComfyUI workflows.

HyperMemory does not require a separate graph ID in this node. The `hm_...` API key is resolved server-side to the tenant and graph it can access. If the key is linked to a specific graph, HyperMemory validates and routes to that graph automatically.

Be careful when sharing ComfyUI workflow JSON files: node input values may be saved in the workflow. Remove API keys before publishing or sending workflows to others.

## Error Handling

The node is designed to keep partial output useful:

- If HyperMemory is disabled or missing a key, extraction and prompt assembly still run.
- If HyperMemory recall fails, `status` explains the issue and OpenRouter can still run with explicit brand details.
- If OpenRouter is disabled, `llm_output` returns the assembled prompt.
- If OpenRouter fails, `llm_output` contains the provider error and the intermediate outputs remain available.

## Development

Run the local checks:

```bash
python3 -m py_compile core.py nodes.py __init__.py tests/test_core.py
python3 -m unittest discover -s tests -v
```

Current coverage includes:

- regex extraction modes matching the ComfyUI baseline,
- invalid regex and no-match behavior,
- HyperMemory recall request shape and context formatting,
- OpenRouter default model and request payload behavior.

## Project Structure

```text
.
├── __init__.py        # ComfyUI exports
├── core.py            # extraction, HyperMemory, OpenRouter, prompt helpers
├── nodes.py           # ComfyUI V3 node definition
├── requirements.txt   # no external dependencies
└── tests/
    └── test_core.py
```

## License

MIT. See [LICENSE](LICENSE).
