import asyncio
import os

import httpx
from fastapi import HTTPException
from litellm.integrations.custom_logger import CustomLogger

# Request never reached/finished on classifier; safe to retry (classification has no side effects)
RETRYABLE_ERRORS = (httpx.ConnectError, httpx.RemoteProtocolError)


class LayaClassifierCallback(CustomLogger):
    def __init__(self):
        self.laya_url = os.getenv("LAYA_URL", "http://localhost:8085/prompt/classification")
        timeout = httpx.Timeout(
            float(os.getenv("LAYA_TIMEOUT", "30")),
            connect=float(os.getenv("LAYA_CONNECT_TIMEOUT", "2")),
        )
        self.max_attempts = 2
        self.retry_backoff = float(os.getenv("LAYA_RETRY_BACKOFF", "0.5"))
        # DO not route localhost classifier calls through http(s)_proxy env vars
        self.client = httpx.AsyncClient(trust_env=False, timeout=timeout)

    async def _classify(self, prompt):
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await self.client.post(self.laya_url, json={"prompt": prompt})
            except RETRYABLE_ERRORS as e:
                if attempt == self.max_attempts:
                    raise
                print(f"[LAYA WARN] Classifier call failed ({type(e).__name__}), retrying...")
                await asyncio.sleep(self.retry_backoff)

    # proxy hook for pre-call processing
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        messages = data.get("messages", [])
        print(f"\n[LAYA DEBUG] Pre-API Call: {call_type} with messages: {messages}")
        if not messages:
            return data
            
        user_prompt = messages[-1].get("content", "")
        print(f"\n[LAYA DEBUG] Evaluating prompt: {user_prompt[:50]}...")

        try:
            response = await self._classify(user_prompt)
        except httpx.TransportError as e:
            print(f"[LAYA ERROR] Classifier Unavailable: {type(e).__name__}: {e} ")
            raise HTTPException(
                status_code=503,
                detail={"error": "Laya Classifier unavailable."},
            ) from e
        
        # Fail closed: never fwd a prompt that was not successfully classified
        if response.status_code != 200:
            print(f"[LAYA ERROR] Classifier returned HTTP {response.status_code}: {response.text[:200]}")
            raise HTTPException(
                status_code=502,
                detail={"error": "Laya classifier returned an error."}
            )

        try:
            laya_output = response.json()
            if not isinstance(laya_output, dict):
                raise ValueError(f"Expected JSON response, got {type(laya_output).__name__}")
        except ValueError as e:
            print(f"[LAYA ERROR] Invalid classifier response: {e}")
            raise HTTPException(
                status_code=502,
                detail={"error": "Laya classifier returned invalid response."}
            ) from e

        # --- DISPLAY LAYA OUTPUT CLEARLY ---
        print("\n" + "="*50)
        print(f"[LAYA] Full JSON Response: {laya_output}")
        print(f"[LAYA] Unsafe Value Checked: '{laya_output.get('unsafe')}'")
        print("="*50 + "\n")
                
        # --- GUARANTEED BLOCKING TRIGGER ---
        # Normalize string comparison to catch variations ("yes", "Yes", "yes ")
        is_unsafe = str(laya_output.get("unsafe", "")).strip().lower() == "yes"
                
        if is_unsafe:
            print("[LAYA TRIGGERED] Unsafe prompt confirmed! Blocking request...")
            raise HTTPException(
                status_code=400,
                detail={"error": "Prompt classified as unsafe. Request blocked by security protocol."}
            )
                
        # Handle routing/metadata additions if clean
        if "metadata" not in data:
             data["metadata"] = {}
        data["metadata"]["laya_rag"] = laya_output.get("rag")
        data["metadata"]["laya_reasoning"] = laya_output.get("reasoning")
                
        tier = laya_output.get("model_tier", "routine")
        if tier == "routine":
            data["model"] = "qwen-local"
        else:
            data["model"] = "qwen-local"

        return data

# Create the instance to be imported
laya_callback = LayaClassifierCallback()
