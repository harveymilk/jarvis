from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI()


def call_openai(messages: list[dict], model: str = "gpt-4o", temperature: float = 1.0, **kwargs) -> str:
    """
    Call the OpenAI API with a given prompt.
    """

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs
    )
    return response.choices[0].message.content