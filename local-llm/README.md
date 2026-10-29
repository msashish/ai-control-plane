# Local LLM

    LLM at your place. No internet. No cost.

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
    cd local-llm
    mkdir -p models
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
        Start Ollama server and register local model
            OLLAMA_HOST="127.0.0.1:8081" ollama serve

        From another terminal:
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

