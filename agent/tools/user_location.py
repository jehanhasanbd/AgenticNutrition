import requests, os
from typing import Optional, Dict, Any
from dotenv import load_dotenv  # ← Add this
from langchain_core.tools import tool

load_dotenv()
LOCATION_API = os.getenv("LOCATION_API")


@tool("get_user_location")
def get_user_location(country_hint: Optional[str]=None) -> Dict[str, Any]:
    """
        Get approximate user location using IP-based geolocation.
        No API key required (uses https://app.ipgeolocation.io/api). If it fails, returns unknown.
        """
    try:
        """Get the geographical location data for an IP address."""
        resp = requests.get(
            f"https://api.ipgeolocation.io/ipgeo?apiKey={LOCATION_API}&ip=160.202.144.36",
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        return {
            "status": "ok",
            "city": data.get("city"),
            "region": data.get("state_prov"),
            "country": data.get("country_name"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("time_zone", {}).get("name"),
            "source":"https://app.ipgeolocation.io/api",
            "note": "Approximate IP-based location."
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "city": None,
            "region": None,
            "country": country_hint,
            "latitude": None,
            "longitude": None,
            "timezone": None
        }