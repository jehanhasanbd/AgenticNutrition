import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

load_dotenv()

def get_llm_instance():
    """
        This is the llm calling

        Generic LLM loader.

        Supported providers:
        - openai
        - anthropic
        - gemini
        - ollama
    """
    provider = os.getenv("LLM_PROVIDER",'openai').lower()
    model = os.getenv("LLM_MODEL",'gpt-5.2')
    temperature = (os.getenv("LLM_TEMPERATURE","0.2"))

    if provider == 'openai':
        return ChatOpenAI(model=model, temperature=temperature)
    elif provider == 'anthropic':
        return ChatAnthropic(model=model,temperature=temperature)
    elif provider == 'gemini':
        return ChatGoogleGenerativeAI(model=model,temperature=temperature)
    elif provider == 'ollama':
        return ChatOllama(model=model,temperature=temperature)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_embedding_model():
    """
        Generic embedding model loader.
    """
    provider = os.getenv("EMBEDDING_PROVIDER","openai").lower()
    model = os.getenv("EMBEDDING_MODEL","text-embedding-3-small")
    if provider == 'openai':
        return OpenAIEmbeddings(model=model)
    else:
        raise ValueError(
            f"Unsupported embedding provider: {provider}"
        )

