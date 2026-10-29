import httpx
from litellm.integrations.custom_logger import CustomLogger
from litellm.exceptions import APIError

class LayaClassifierCallback(CustomLogger):
    def __init__(self):
        self.laya_url = "http://localhost:8085/prompt/classification"

    async def async_log_pre_api_call(self, user_api_key_dict, cache_dict, data, call_type):
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
                    timeout=2.0
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
                    print("[LAYA TRIGGERED] Unsafe prompt confirmed! Raising APIError to block request...")
                    raise APIError(
                        status_code=400,
                        message="Request blocked by Laya security protocol.",
                        llm_provider="LayaSecurityGateway"
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
                    
        except APIError:
            # Pass this through cleanly so LiteLLM intercepts it as a terminal routing failure
            raise
        except Exception as e:
            print(f"[LAYA ERROR] Callback pipeline failure: {str(e)}")
            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"]["laya_error"] = str(e)
            data["model"] = "qwen-local"
            
        return data

# Create the instance to be imported
laya_callback = LayaClassifierCallback()
