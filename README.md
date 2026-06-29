# hypermemory-cumfyui-extract-text-node

A ComfyUI custom node that forks ComfyUI's `Extract Text` regex behavior and adds HyperMemory brand recall plus OpenRouter prompt generation.

The main use case is marketing video prompt generation: extract a useful phrase or brief, recall brand context from HyperMemory, and generate a polished on-brand prompt through OpenRouter.

## Install

Clone this repo into your ComfyUI custom nodes directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RunStack-AI/hypermemory-cumfyui-extract-text-node.git
```

Restart ComfyUI after cloning.

## Node

`HyperMemory Extract Text` appears under `text/HyperMemory`.

It preserves ComfyUI's upstream `Extract Text` regex modes:

- `First Match`
- `All Matches`
- `First Group`
- `All Groups`

After extraction, it can:

- recall brand context from HyperMemory using the HyperMemory REST API used by the CLI,
- assemble a brand-aware prompt,
- call OpenRouter to produce the final generation prompt.

## API Keys

The node accepts keys as inputs:

- `hypermemory_api_key`
- `openrouter_api_key`

No graph ID is required. HyperMemory `hm_...` API keys are resolved server-side to the tenant/graph they are allowed to access.

## Defaults

- HyperMemory API URL: `https://api.hypermemory.io`
- HyperMemory endpoint: `/api/v1/memory/recall`
- OpenRouter model: `minimax/minimax-m3`
- Temperature: `0.4`
- Max tokens: `900`

## Outputs

- `extracted_text`: regex extraction result.
- `memory_context`: formatted HyperMemory recall results.
- `assembled_prompt`: prompt sent to OpenRouter.
- `llm_output`: final prompt or setup/error text.
- `status`: concise execution status.

## Workflow Pattern

1. Paste or wire source text into `string`.
2. Configure the regex extraction pattern and mode.
3. Add HyperMemory and OpenRouter API keys.
4. Add explicit `brand_details`.
5. Use `llm_output` for CLIP/video generation, or inspect `assembled_prompt` before generation.
