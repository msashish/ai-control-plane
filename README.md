# AI Control plane

| Service | port | purpose |
| --- | --- | --- |
| `ai-gateway` | `4000` | `Orchestrate/route prompts using Litellm` |
| `classifier` | `8085` | `FastAPI server with local laya weights service` |
| `local LLM` | `8081` | `LLM inference server serving a local model` |

## Local test

Pre-requisites: `uv`, `curl` and model gguf at `local-llm/models/qwen.gguf`

From repo root:
    make
        up                 Start llm (ollama) -> classifier -> gateway -> ui
        down               Stop all services
        restart            down + up
        test               Run ai-gateway/tests
        status             Show status of all services