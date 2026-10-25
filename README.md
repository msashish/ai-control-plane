# LLM Router

## Local Setup

1. **Setup python virtual env**

    ```bash
    uv sync
    source .venv/bin/activate
    ```

2. **Download Laya classifier checkpoint (one time)**

    ```bash
    uv pip install modelscope
    ..or..
    uv add modelscope

    python -c "from modelscope import snapshot_download; snapshot_download('convaiinnovations/laya', local_dir='./laya_weights')"
    ```

    Note: I am avoiding direct huggingface url. Hence router loads laya_weights directory. 

