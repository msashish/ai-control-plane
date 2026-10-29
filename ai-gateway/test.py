import litellm

response = litellm.completion(
    model="ollama/my-qwen",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    api_base="http://localhost:8081"
)

print(response.choices[0].message.content)
