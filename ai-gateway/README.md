# ai-gateway

    AI Gateway using LLMlite

## Setup local model & inference engine

   Refer to local-llm/README.md

   listens on port 8081

## Setup local Classifier service

    Refer to classifier/README.md
    cd classifier
    uv run fastapi run --port 8085

    listens on port 8085

## Setup llmlite AI gateway

    ```bash
    uv tool install 'litellm[proxy]'
    
    Configure at config.yaml

    Start gateway:
        python main.py

        ..or..
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

## Test gateway, classifier and localLLM 

    python test.py