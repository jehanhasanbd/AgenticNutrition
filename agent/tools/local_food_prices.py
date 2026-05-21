import joblib
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional
import datetime

from langchain_core.tools import tool

_model = joblib.load("agent/tools/food_price_model.pkl")


class FoodPricePredictionInput(BaseModel):
    place: str = Field(
        description=(
            "The admin2 district/city name in Bangladesh where the price is "
            "needed (e.g. 'Dhaka', 'Chittagong', 'Sylhet')."
        )
    )

    product: str = Field(
        description=(
            "The commodity name exactly as used in training data "
            "(e.g. 'Rice (coarse, BR-8/ 11/, Guti Sharna)', "
            "'Wheat', 'Lentils (masur)')."
        )
    )

    latitude: Optional[float] = Field(
        default=None,
        description=(
            "Latitude of the market location "
            "(e.g. 23.81 for Dhaka). Optional."
        )
    )

    longitude: Optional[float] = Field(
        default=None,
        description=(
            "Longitude of the market location "
            "(e.g. 90.41 for Dhaka). Optional."
        )
    )

    date: Optional[str] = Field(
        default=None,
        description=(
            "Date for the prediction in YYYY-MM-DD format. "
            "Defaults to today if not provided."
        )
    )


@tool("get_local_food_prices", args_schema=FoodPricePredictionInput)
def get_local_food_prices(
    place: str,
    product: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    date: Optional[str] = None
) -> str:
    """
    Predict the wholesale food price (in BDT per KG) for a given commodity,
    location, and date in Bangladesh using a trained XGBoost regression model.

    Returns the predicted price as a human-readable string.
    """

    # ---------------- Date Handling ----------------
    if date:
        try:
            parsed_date = datetime.datetime.strptime(
                date,
                "%Y-%m-%d"
            )
        except ValueError:
            return (
                f"Invalid date format '{date}'. "
                "Please use YYYY-MM-DD "
                "(e.g. '2025-06-15')."
            )
    else:
        parsed_date = datetime.datetime.today()

    year = parsed_date.year
    month = parsed_date.month
    day = parsed_date.day

    # ---------------- Fallback Coordinates ----------------
    # Dhaka default
    if latitude is None:
        latitude = 23.8103

    if longitude is None:
        longitude = 90.4125

    # ---------------- Model Input ----------------
    input_df = pd.DataFrame([{
        "place": place,
        "product": product,
        "latitude": latitude,
        "longitude": longitude,
        "year": year,
        "month": month,
        "day": day,
    }])

    # ---------------- Prediction ----------------
    try:
        predicted_price = _model.predict(input_df)[0]

    except Exception as e:
        return (
            f"Prediction failed: {e}\n"
            "Check that 'place' and 'product' "
            "match values seen during training."
        )

    return (
        f"Predicted wholesale price for '{product}' in {place} "
        f"on {parsed_date.strftime('%B %d, %Y')}: "
        f"BDT {predicted_price:,.2f} per KG"
    )