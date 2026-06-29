# HyperMemory ComfyUI Extract Text Node

ComfyUI's `Extract Text` node, with HyperMemory brand context and OpenRouter prompt refinement behind the scenes.

![ComfyUI](https://img.shields.io/badge/ComfyUI-custom_node-111111)
![HyperMemory](https://img.shields.io/badge/HyperMemory-brand_context-4f46e5)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM_prompts-10b981)
![Python](https://img.shields.io/badge/Python-stdlib_only-3776ab)
![License](https://img.shields.io/badge/License-MIT-f59e0b)

## What It Does

`Extract Text - Hypermemory` keeps the same simple shape as ComfyUI's built-in `Extract Text` node:

- visible inputs: `string`, `regex_pattern`, `mode`
- advanced regex settings: `case_insensitive`, `multiline`, `dotall`, `group_index`
- output: one `STRING`

The node first extracts text using the normal regex behavior. If HyperMemory and OpenRouter are configured outside the workflow, it uses the extracted text to recall brand context from HyperMemory and asks OpenRouter to turn it into an on-brand prompt.

If credentials are not configured, it falls back to plain extracted text.

## Install

Clone this repo into your ComfyUI custom nodes folder:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RunStack-AI/hypermemory-cumfyui-extract-text-node.git
```

Restart ComfyUI. The node appears as:

```text
text/HyperMemory -> Extract Text - Hypermemory
```

No extra Python packages are required.

## Configuration

Do not put API keys into workflow nodes. Set them in the environment before starting ComfyUI:

```bash
export HYPERMEMORY_API_KEY="hm_..."
export OPENROUTER_API_KEY="..."
```

Optional environment settings:

```bash
export HYPERMEMORY_API_URL="https://api.hypermemory.io"
export HYPERMEMORY_MAX_RESULTS="10"
export OPENROUTER_MODEL="minimax/minimax-m3"
export OPENROUTER_TEMPERATURE="0.4"
export OPENROUTER_MAX_TOKENS="900"
```

No graph ID is required. HyperMemory resolves the graph from the `hm_...` API key.

Brand details should live in HyperMemory. Store voice, audience, palette, product rules, campaign history, and visual constraints in the graph instead of entering them in the node UI.

## How To Use

### 1. Add The Node

In ComfyUI, right-click the canvas and add:

```text
text/HyperMemory -> Extract Text - Hypermemory
```

### 2. Add Source Text

Paste or connect the rough text into `string`.

Example:

```text
Campaign brief: 15 second teaser for the new running shoe line.
Focus on speed, city lights, and premium performance.
```

### 3. Extract The Useful Part

Set `regex_pattern` and `mode`.

Example regex:

```regex
Campaign brief:\s*(.*)
```

Recommended mode:

```text
First Group
```

Extracted text:

```text
15 second teaser for the new running shoe line.
```

Common patterns:

| Goal | Regex | Mode |
|---|---|---|
| Text after a label | `Brief:\s*(.*)` | `First Group` |
| Every hashtag | `#(\w+)` | `All Groups` |
| First quoted phrase | `"([^"]+)"` | `First Group` |
| First URL | `https?://\S+` | `First Match` |
| Numbered lines | `^\d+\.\s*(.*)` | `All Groups` with `multiline` on |

### 4. Wire The Output

The node has one output. Use it where prompt text belongs:

```text
Extract Text - Hypermemory -> CLIP Text Encode.text
```

With `HYPERMEMORY_API_KEY` and `OPENROUTER_API_KEY` configured, that output is the refined brand prompt. Without them, it is the extracted text.

## Inputs And Output

| Name | Type | Notes |
|---|---|---|
| `string` | input | Source text. |
| `regex_pattern` | input | Regex pattern. |
| `mode` | input | Defaults to `First Group`. |
| `STRING` | output | Extracted text or refined prompt. |

Advanced regex controls match the source Extract Text node: `case_insensitive`, `multiline`, `dotall`, and `group_index`.

## Failure Behavior

- Regex does not match: output is empty, matching the source node.
- HyperMemory is not configured or fails: the node continues without memory context.
- OpenRouter is not configured or fails: the node returns the best local output available.

## Development

Run the local checks:

```bash
python3 -m py_compile core.py nodes.py __init__.py tests/test_core.py
python3 -m unittest discover -s tests -v
```

## Project Structure

```text
.
├── __init__.py        # ComfyUI exports
├── core.py            # extraction, HyperMemory, OpenRouter, prompt helpers
├── nodes.py           # ComfyUI node definition
├── requirements.txt   # no external dependencies
└── tests/
    └── test_core.py
```

## License

MIT. See [LICENSE](LICENSE).
