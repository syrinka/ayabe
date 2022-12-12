from pydantic import BaseModel


class Config(BaseModel):
    openai_api_key: str
    chatgpt_model: str = 'text-davinci-003'
    chatgpt_max_tokens: int = 500
    chatgpt_temperature: float = 0.9

