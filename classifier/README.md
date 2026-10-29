# LLM Classifier

![LLM Classification](./llm-router-snap.png)

## Local Setup

1. **Setup python virtual env**

    ```bash
    uv sync
    source .venv/bin/activate

    (uv expects virtual env named .venv)
    ```


2. **Download Laya classifier checkpoint (one time)**

    ```bash
    uv pip install modelscope
    ..or..
    uv add modelscope

    python -c "from modelscope import snapshot_download; snapshot_download('convaiinnovations/laya', local_dir='./classifier/laya_weights')"
    ```

    Note: I am avoiding direct huggingface url. Hence router loads laya_weights directory. 

3. **Run basic classifier test**

    ```bash
    HF_HUB_OFFLINE=1 python test.py
    ```

## Run basic UI

    ```bash
    uv run streamlit run lite.py
    ```

    open at http://localhost:8501

## Run fastapi

    ```bash
    uv run fastapi dev

    ..or in production mode..
    uv run fastapi run --port 8085

    ..or..
    python main.py
    ```

    Try a prompt at:
        http://localhost:8000/docs#/default/classify_prompt_prompt_classification_post


## Get llmlite AI gateway

    ```bash
    uv tool install 'litellm[proxy]'
    ```
    export OPENAI_API_KEY="your-api-key"

    litellm --config config.yaml
    ..or..
    docker run \
        -v $(pwd)/litellm_config.yaml:/app/config.yaml \
        -e OPENAI_API_KEY=<your-openai-key> \
        -e LITELLM_MASTER_KEY=sk-<paste-a-long-random-key> \
        -p 4000:4000 \
        docker.litellm.ai/berriai/litellm:latest \
        --config /app/config.yaml
