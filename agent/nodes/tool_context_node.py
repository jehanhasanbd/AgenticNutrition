from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from agent.state import AgentState
from agent.tools import (
    get_user_location,
    get_weather_and_season,
    get_local_food_prices
)

def tool_context_node(state: AgentState, config:RunnableConfig) -> Dict[str, Any]:
    """
        Calls tools to get location -> weather/season -> local prices (CSV) context.
    """
    thread_id = str(config.get("configurable",{}).get("thread_id","default"))
    user_profile = state.get("user_profile",{}) or {}

    manual_location = user_profile.get("manual_location")   # Dhaka
    hemisphere = user_profile.get("hemisphere","north")

    #-----------------------------------------------
    #    Location
    #-----------------------------------------------

    location = {}
    if manual_location:
        # If user provided a manual location string, we won't geocode here; keep it simple.
        location = {
            "status":"ok",
            "city": manual_location,
            "country": user_profile.get("country"),
            "latitude": None,
            "longitude": None
        }
    else:
        location = get_user_location.invoke({"country_hint": user_profile.get("country")})

    #--------------------------------------------------------
    #    Weather    [Only call weather if we have lat/lon]
    #---------------------------------------------------------
    weather = {}
    if location.get("latitude") is not None and location.get("longitude") is not None:
        weather = get_weather_and_season.invoke({
                "latitude": float(location['latitude']),
                "longitude": float(location['longitude']),
                "hemisphere": hemisphere
            }
        )
    else:
        weather = {
            "status": "ok",
            "season": user_profile.get("season_hint","unknown"),
            "note": "No lat/lon available."
        }

    #--------------------------------------------------------
    #    Prices
    #---------------------------------------------------------

    price_location = location.get("city") or manual_location or "Dhaka"

    prices = get_local_food_prices.invoke({
        "location_name":price_location
    })

    tool_context = {
        "location": location,
        "weather" : weather,
        "prices": prices
    }
    return {
        "tool_context" : tool_context
    }