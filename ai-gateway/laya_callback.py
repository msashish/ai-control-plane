import os

import httpx
from fastapi import HTTPException
from litellm.integrations.custom_logger import CustomLogger

class LayaClassifierCallback(CustomLogger):
    def __init__(self):
        self.laya_url = os.getenv("LAYA_URL", "http://localhost:8085/prompt/classification")
        self.timeout = float(os.getenv("LAYA_TIMEOUT", "30"))  # Default timeout of 30 seconds

    # proxy hook for pre-call processing
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        messages = data.get("messages", [])
        print(f"\n[LAYA DEBUG] Pre-API Call: {call_type} with messages: {messages}")
        if not messages:
            return data
            
        user_prompt = messages[-1].get("content", "")
        print(f"\n[LAYA DEBUG] Evaluating prompt: {user_prompt[:50]}...")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.laya_url, 
                    json={"prompt": user_prompt}, 
                    timeout=self.timeout
                )
                
            if response.status_code == 200:
                laya_output = response.json()

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
                    
        except HTTPException:
            # Pass this through cleanly so LiteLLM intercepts it as a terminal routing failure
            raise
        except Exception as e:
            print(f"[LAYA ERROR] Callback pipeline failure: {str(e)}")
            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"]["laya_error"] = str(e)
            data["model"] = "qwen-local"
            raise HTTPException(
                status_code=500,
                detail={"error": f"Internal error in Laya callback: {str(e)}"}
            )
            
        return data

# Create the instance to be imported
laya_callback = LayaClassifierCallback()
