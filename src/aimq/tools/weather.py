"""Tool for getting weather information using Open-Meteo API."""

import logging
from typing import Any, Dict, Type

import requests
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WeatherInput(BaseModel):
    """Input for Weather tool."""

    location: str = Field(
        ...,
        description="Location to get weather for (city name, address, or coordinates)",
    )


class Weather(BaseTool):
    """Tool for getting current weather information.

    Uses the Open-Meteo API (free, no API key required) to fetch weather data.
    Accepts natural language location queries.

    Example:
        tool = Weather()
        result = tool.run("San Francisco")
        result = tool.run("weather in New York tomorrow")
    """

    name: str = "weather"
    description: str = (
        "Get current weather information for any location. "
        "Accepts city names, addresses, or natural language queries. "
        "Returns temperature, conditions, humidity, and wind speed."
    )
    args_schema: Type[BaseModel] = WeatherInput

    def _geocode(self, location: str) -> Dict[str, Any]:
        """Geocode a location string to coordinates.

        Args:
            location: Location string (city name, address, etc.)

        Returns:
            Dict with latitude, longitude, and location name

        Raises:
            ValueError: If location cannot be geocoded
        """
        try:
            url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {"name": location, "count": 1, "language": "en", "format": "json"}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("results"):
                raise ValueError(f"Location not found: {location}")

            result = data["results"][0]
            return {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "name": result["name"],
                "country": result.get("country", ""),
                "admin1": result.get("admin1", ""),
            }

        except requests.RequestException as e:
            logger.error(f"Geocoding failed: {e}")
            raise ValueError(f"Failed to geocode location: {str(e)}")

    def _get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get weather data for coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dict with weather data

        Raises:
            ValueError: If weather data cannot be fetched
        """
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m",
                ],
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})
            return {
                "temperature": current.get("temperature_2m"),
                "feels_like": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "precipitation": current.get("precipitation"),
                "weather_code": current.get("weather_code"),
            }

        except requests.RequestException as e:
            logger.error(f"Weather fetch failed: {e}")
            raise ValueError(f"Failed to fetch weather data: {str(e)}")

    def _weather_code_to_description(self, code: int) -> str:
        """Convert WMO weather code to description.

        Args:
            code: WMO weather code

        Returns:
            Human-readable weather description
        """
        codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }
        return codes.get(code, "Unknown")

    def _run(self, location: str) -> str:
        """Get weather for a location.

        Args:
            location: Location string (natural language accepted)

        Returns:
            Formatted weather information string
        """
        try:
            geo = self._geocode(location)
            weather = self._get_weather(geo["latitude"], geo["longitude"])

            location_name = geo["name"]
            if geo.get("admin1"):
                location_name += f", {geo['admin1']}"
            if geo.get("country"):
                location_name += f", {geo['country']}"

            conditions = self._weather_code_to_description(weather["weather_code"])

            result = f"""Weather for {location_name}:
• Temperature: {weather['temperature']}°F (feels like {weather['feels_like']}°F)
• Conditions: {conditions}
• Humidity: {weather['humidity']}%
• Wind Speed: {weather['wind_speed']} mph
• Precipitation: {weather['precipitation']} in"""

            return result

        except ValueError as e:
            logger.error(f"Weather tool error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected weather tool error: {e}", exc_info=True)
            return f"Error getting weather: {str(e)}"
