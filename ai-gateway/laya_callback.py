import httpx
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy._types import ProxyException 

class LayaClassifierCallback(CustomLogger):
    def __init__(self):
        self.laya_url = "http://localhost:8085/prompt/classification"

    async def async_pre_call_hook(self, user_api_key_dict, cache_dict, data, call_type):
        messages = data.get("messages", [])
        if not messages:
            return data
            
        user_prompt = messages[-1].get("content", "")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.laya_url, 
                    json={"prompt": user_prompt}, 
                    timeout=2.0
                )
                
            if response.status_code == 200:
                laya_output = response.json()
                
                # Drop request if unsafe
                if laya_output.get("unsafe") == "yes":
                    raise ProxyException(
                        message="Request blocked by Laya security protocol.",
                        type="security_violation",
                        param="prompt",
                        code=400
                    )
                
                if "metadata" not in data:
                    data["metadata"] = {}
                data["metadata"]["laya_rag"] = laya_output.get("rag")
                data["metadata"]["laya_reasoning"] = laya_output.get("reasoning")
                
                tier = laya_output.get("model_tier", "routine")
                if tier == "routine":
                    data["model"] = "qwen-local"
                else:
                    data["model"] = "qwen-local"
                    
        except ProxyException:
            raise
        except Exception as e:
            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"]["laya_error"] = str(e)
            data["model"] = "qwen-local"
            
        return data

# Create the instance to be imported
laya_callback = LayaClassifierCallback()
