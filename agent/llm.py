from llm_manager import get_llm_instance
from agent.tools import (
    get_user_location,
    get_weather_and_season,
    get_local_food_prices
)

llm = get_llm_instance()

TOOLS = [
    get_user_location,
    get_weather_and_season,
    get_local_food_prices
]

llm_with_tools = llm.bind_tools(TOOLS)
