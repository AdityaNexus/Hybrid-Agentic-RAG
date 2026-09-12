from src.config.settings import settings
from openai import OpenAI

client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
)

def generate(
        prompt:str,
        *,
        system_prompt:str|None=None,
        temperature:float = 0.0,
        max_tokens:int = 512,
)->str:
    messages = []
    if system_prompt:
        messages.append(
            {
                "role":"system",
                "content":system_prompt,
            }
        )
    messages.append({
        "role":"user",
        "content":prompt,
    })

    response = client.chat.completions.create(
        model = settings.llm_model,
        messages = messages,
        temperature = temperature,
        max_tokens = max_tokens,
    )

    return response.choices[0].message.content or ""