from openai import OpenAI

client = OpenAI(
    api_key="any-string",  # Proxy key (can be anything if master_key isn't set)
    base_url="http://0.0.0.0:4000"  # Point directly to LiteLLM gateway
)

response = client.chat.completions.create(
    model="my-local-llama",
    messages=[{"role": "user", "content": "Design a event driven dependency management solution using CloudRun, pubsub and Bigquery for storing control information"}]
)

print(response.choices[0].message.content)
