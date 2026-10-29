# ai-gateway

    AI Gateway using LLMlite

## Setup local model

## Setup local LLM service


## Setup local Classifier service

## Setup llmlite AI gateway

    ```bash
    uv tool install 'litellm[proxy]'
    
    Configure at config.yaml

    litellm --config config.yaml --port 4000

    ..or..
    docker run \
        -v $(pwd)/litellm_config.yaml:/app/config.yaml \
        -e OPENAI_API_KEY=<your-openai-key> \
        -e LITELLM_MASTER_KEY=sk-<paste-a-long-random-key> \
        -p 4000:4000 \
        docker.litellm.ai/berriai/litellm:latest \
        --config /app/config.yaml

    Gateway starts listening from port 4000

    ```