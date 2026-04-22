from openai import AsyncOpenAI
from strands import Agent
from strands.models.openai import OpenAIModel

client = AsyncOpenAI(api_key="<api key>")
agent = Agent(
    model=OpenAIModel(model_id="gpt-5.2", client=client),
)
agent("こんにちは")
