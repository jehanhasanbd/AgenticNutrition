from typing import Dict, Any
import datetime

from langchain_core.runnables import RunnableConfig

from agent.state import AgentState
from agent.tools import (
    get_user_location,
    get_weather_and_season,
    get_local_food_prices
)

DEFAULT_COMMODITIES = [
    'Potatoes (Holland, white)',
    'Wheat flour',
    'Eggs (brown)',
    'Sugar',
    'Oil (palm)',
    'Chili (green)',
    'Gourd (bottle)',
    'Papaya (green)',
    'Spinach (malabar)',
    'Fish (live, pangasius)',
    'Lentils (masur)',
    'Garlic (imported, China)',
    'Onions (imported, China)',
    'Snake gourd',
    'Oil (soybean, fortified)',
    'Rice (coarse)',
    'Meat (chicken, broiler)',
    'Bananas (ripe)',
    'Spinach (red)',
    'Rice (Kajla)',
    'Rice (Nurjahan)',
    'Rice (coarse, BR-8/ 11/, Guti Sharna)',
    'Eggs (white)',
    'Fish (dry, belt 10-12")',
    'Milk (powder)',
    'Chili (whole, dry, Indian Teja)',
    'Hyacinth (sim)',
    'Salt (iodized, Molla)',
    'Dishwashing liquid',
    'Laundry detergent',
    'Toilet paper',
    'Toothpaste',
    'Chickpeas',
    'Bananas (green)',
    'Carrots',
    'Eggplants',
    'Ginger (imported)',
    'Gourd (bitter)',
    'Lemon (medium size)',
    'Oranges (malta)',
    'Pumpkin',
    'Tomatoes (red)',
    'Rice (BRRI-28)',
    'Rice (BRRI-29)',
    'Fish (live, tilapia)',
    'Meat (beef)',
    'Meat (chicken, sonali)',
    'Turmeric (powder, Fresh)',
    'Bathing soap',
    'Fuel (diesel)',
    'Fuel (kerosene)',
    'Handwash soap',
    'Oil (mustard)',
    'Apples (royal gala)',
    'Cabbage',
    'Cucumber (short, khira)',
    'Onions (imported, India)',
    'Rice (Gazi)',
    'Firewood',
    'Fuel (gas)',
    'Sanitary pads',
    'Fish (tilapia, fresh)',
    'Milk',
    'Beans (mung, large grain)',
    'Fuel (petrol)',
    'Cauliflower',
    'Ginger (local)'
]


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def tool_context_node(
    state: AgentState,
    config: RunnableConfig
) -> Dict[str, Any]:
    """
    Calls tools to get:
    location -> weather/season -> local food prices context.
    """

    thread_id = str(
        config.get("configurable", {}).get(
            "thread_id",
            "default"
        )
    )

    user_profile = state.get(
        "user_profile",
        {}
    ) or {}

    manual_location = user_profile.get(
        "manual_location"
    )

    hemisphere = user_profile.get(
        "hemisphere",
        "north"
    )

    # ---------------------------------------------------
    # Location
    # ---------------------------------------------------

    if manual_location:
        location = {
            "status": "ok",
            "city": manual_location,
            "country": user_profile.get("country"),
            "latitude": None,
            "longitude": None,
        }

    else:
        location = get_user_location.invoke({
            "country_hint": user_profile.get(
                "country"
            )
        })

    latitude = safe_float(
        location.get("latitude")
    )

    longitude = safe_float(
        location.get("longitude")
    )

    # ---------------------------------------------------
    # Weather
    # ---------------------------------------------------

    if latitude is not None and longitude is not None:

        weather = get_weather_and_season.invoke({
            "latitude": latitude,
            "longitude": longitude,
            "hemisphere": hemisphere
        })

    else:
        weather = {
            "status": "ok",
            "season": user_profile.get(
                "season_hint",
                "unknown"
            ),
            "note": "No lat/lon available."
        }

    # ---------------------------------------------------
    # Prices
    # ---------------------------------------------------

    price_location = (
        location.get("city")
        or manual_location
        or "Dhaka"
    )

    today = datetime.datetime.today().strftime(
        "%Y-%m-%d"
    )

    predicted_prices = []

    for product in DEFAULT_COMMODITIES:

        tool_input = {
            "place": price_location,
            "product": product,
            "date": today,
        }

        # Only pass lat/lon if valid
        if latitude is not None:
            tool_input["latitude"] = latitude

        if longitude is not None:
            tool_input["longitude"] = longitude

        try:
            prediction = get_local_food_prices.invoke(
                tool_input
            )

        except Exception as e:
            prediction = (
                f"Prediction failed for "
                f"{product}: {str(e)}"
            )

        predicted_prices.append({
            "product": product,
            "price": prediction
        })

    # ---------------------------------------------------
    # Final Tool Context
    # ---------------------------------------------------

    tool_context = {
        "location": location,
        "weather": weather,
        "prices": predicted_prices
    }

    return {
        "tool_context": tool_context
    }