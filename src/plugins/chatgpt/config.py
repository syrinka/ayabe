from pydantic import BaseSettings, Extra


class Config(BaseSettings, extra=Extra.ignore):
    openai_api_key: str
    chatgpt_model: str = 'text-davinci-003'
    chatgpt_max_tokens: int = 500
    chatgpt_temperature: float = 0.9
