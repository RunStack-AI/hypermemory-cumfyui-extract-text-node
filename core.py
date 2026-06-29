import json
import re
import urllib.error
import urllib.request


DEFAULT_HYPERMEMORY_API_URL = "https://api.hypermemory.io"
DEFAULT_OPENROUTER_MODEL = "minimax/minimax-m3"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_SYSTEM_PROMPT = (
    "You are a marketing video prompt writer. Generate detailed, cinematic "
    "video generation prompts optimized for AI video models. Include camera "
    "movements, lighting, color grading, pacing, and mood. Stay on-brand "
    "based on the provided context."
)


class HyperMemoryError(RuntimeError):
    pass


class OpenRouterError(RuntimeError):
    pass


def extract_text(
    string,
    regex_pattern,
    mode,
    case_insensitive=True,
    multiline=False,
    dotall=False,
    group_index=1,
):
    join_delimiter = "\n"
    flags = 0

    if case_insensitive:
        flags |= re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE
    if dotall:
        flags |= re.DOTALL

    try:
        if mode == "First Match":
            match = re.search(regex_pattern, string, flags)
            if match:
                return match.group(0)
            return ""

        if mode == "All Matches":
            matches = re.findall(regex_pattern, string, flags)
            if matches:
                if isinstance(matches[0], tuple):
                    return join_delimiter.join([m[0] for m in matches])
                return join_delimiter.join(matches)
            return ""

        if mode == "First Group":
            match = re.search(regex_pattern, string, flags)
            if match and len(match.groups()) >= group_index:
                return match.group(group_index)
            return ""

        if mode == "All Groups":
            matches = re.finditer(regex_pattern, string, flags)
            results = []
            for match in matches:
                if match.groups() and len(match.groups()) >= group_index:
                    results.append(match.group(group_index))
            return join_delimiter.join(results)

        return ""
    except re.error:
        return ""


def _json_request(url, payload, headers, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            **headers,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_text = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {details}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(str(exc)) from exc

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON response: {response_text[:500]}") from exc


def recall_hypermemory(api_key, api_url, query, max_results=10):
    api_key = api_key.strip()
    query = query.strip()
    api_url = (api_url or DEFAULT_HYPERMEMORY_API_URL).strip().rstrip("/")

    if not api_key:
        raise HyperMemoryError("HyperMemory API key is required when memory recall is enabled.")
    if not query:
        return {}

    try:
        return _json_request(
            f"{api_url}/api/v1/memory/recall",
            {"query": query, "max_results": int(max_results)},
            {"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
    except RuntimeError as exc:
        message = str(exc)
        if "HTTP 401" in message or "HTTP 403" in message:
            raise HyperMemoryError("HyperMemory API key is invalid or unauthorized for this graph.") from exc
        raise HyperMemoryError(f"HyperMemory recall failed: {message}") from exc


def format_hypermemory_context(response):
    results = response.get("results", []) if isinstance(response, dict) else []
    if not results:
        return ""

    blocks = []
    for index, result in enumerate(results, start=1):
        if not isinstance(result, dict):
            continue

        key = result.get("key", "")
        description = result.get("description", "")
        score = result.get("score")
        header_parts = [f"[{index}]"]
        if key:
            header_parts.append(str(key))
        if score is not None:
            header_parts.append(f"(score: {score})")

        lines = [" ".join(header_parts)]
        if description:
            lines.append(str(description))

        expansion = result.get("expansion_context") or []
        related_lines = []
        for item in expansion:
            if not isinstance(item, dict):
                continue
            rel = item.get("rel", "")
            rel_key = item.get("key", "")
            rel_desc = item.get("description", "")
            related = " - ".join([part for part in [rel_key, rel, rel_desc] if part])
            if related:
                related_lines.append(f"- {related}")

        if related_lines:
            lines.append("Related context:")
            lines.extend(related_lines)

        blocks.append("\n".join(lines).strip())

    return "\n\n".join(blocks).strip()


def assemble_prompt(extracted_text, brand_details, memory_context):
    sections = [
        "Create one production-ready AI video or image generation prompt from the extracted text.",
        "Return only the final prompt. Do not include markdown, labels, or explanation.",
    ]

    if brand_details.strip():
        sections.append(f"Brand details and constraints:\n{brand_details.strip()}")

    if memory_context.strip():
        sections.append(f"Relevant HyperMemory brand context:\n{memory_context.strip()}")

    sections.append(f"Extracted text:\n{extracted_text.strip()}")
    return "\n\n".join(sections).strip()


def call_openrouter(api_key, model, system_prompt, prompt, temperature=0.4, max_tokens=900):
    api_key = api_key.strip()
    if not api_key:
        raise OpenRouterError("OpenRouter API key is required when generation is enabled.")

    payload = {
        "model": (model or DEFAULT_OPENROUTER_MODEL).strip() or DEFAULT_OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt or DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }

    try:
        response = _json_request(
            OPENROUTER_URL,
            payload,
            {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/RunStack-AI/hypermemory-cumfyui-extract-text-node",
                "X-Title": "HyperMemory ComfyUI Extract Text Node",
            },
            timeout=90,
        )
    except RuntimeError as exc:
        raise OpenRouterError(f"OpenRouter request failed: {exc}") from exc

    error = response.get("error")
    if error:
        if isinstance(error, dict):
            message = error.get("message") or json.dumps(error, sort_keys=True)
        else:
            message = str(error)
        raise OpenRouterError(message)

    choices = response.get("choices") or []
    if not choices:
        raise OpenRouterError("OpenRouter returned no choices.")

    message = choices[0].get("message") or {}
    return (message.get("content") or "").strip()
