# ai-gateway

    AI Gateway using LLMlite

## Setup local model inference engine

    brew install ollama

    If you want llama:
        Pull llama.cpp server. Acts as model inference engine

        Without docker: 
            curl -LsSf https://llama.app/install.sh | sh

        With docker: 
            docker pull ghcr.io/ggml-org/llama.cpp:server

## Setup local LLM service

1. Get a model GGUF
    cd ai-gateway
    curl -L \
        -o models/qwen.gguf \
        https://modelscope.cn/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/master/qwen2.5-0.5b-instruct-q4_k_m.gguf

    ..or.. if huggingface.io is accesible

    curl -L \
        -o models/qwen.gguf \
        https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/master/qwen2.5-0.5b-instruct-q4_k_m.gguf

2. Verify
    file models/qwen.gguf # should say "data", not "HTML document"
    head -c 4 models/qwen.gguf # should print GGUF

3. Start model inference server

    Using Ollama:
        Start Ollama server
            OLLAMA_HOST="127.0.0.1:8081" ollama serve

        Register local model from another terminal:
            OLLAMA_HOST="127.0.0.1:8081" ollama create my-qwen -f ./Modelfile

        Test run
            OLLAMA_HOST="127.0.0.1:8081" ollama run my-qwen
            ctrl d or /bye to exit

        Open API:
            curl http://localhost:8081/v1/chat/completions \
            -H "Content-Type: application/json" \
            -d '{
                "model": "my-qwen",
                "messages": [{"role": "user", "content": "Whats capital of India?"}]
            }'


    Docker mode: 
        docker run --rm \
        -p 8081:8080 \
        -v $(pwd)/models:/models \
        ghcr.io/ggml-org/llama.cpp:server \
        -m /models/qwen.gguf \
        --host 0.0.0.0

    LLM service is now listening at 8081

4. Test inference

    curl http://localhost:8081/completion \
        -H "Content-Type: application/json" \
        -d '{
                "prompt": "What is GGUF?",
                "n_predict":50
        }'
        ``

## Setup local Classifier service

    Refer to classifier/README.md

    Run API mode with classifier listening on port 8085

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