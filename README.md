# AI Control plane

| Service | port | purpose |
| --- | --- | --- |
| `ai-gateway` | `4000` | `Orchestrate/route prompts using Litellm` |
| `classifier` | `8085` | `FastAPI server with local laya weights service` |
| `local LLM` | `8081` | `LLM inference server serving a local model` |
