from dotenv import load_dotenv
import os
import requests

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from langgraph.prebuilt import create_react_agent

# Load env variables
load_dotenv()

# Read API key
api_key = os.getenv("OPENROUTER_API_KEY")

# Initialize model
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# TOOL
@tool
def get_weather(city: str):
    """
    Get weather of a city.
    """

    try:

        # Convert city to coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"

        geo_response = requests.get(geo_url, timeout=10)

        geo_data = geo_response.json()

        if "results" not in geo_data:
            return "City not found."

        latitude = geo_data["results"][0]["latitude"]
        longitude = geo_data["results"][0]["longitude"]

        # Get weather
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            f"&daily=temperature_2m_max,temperature_2m_min"
             "&forecast_days=2"
             "&timezone=auto"
        )

        weather_response = requests.get(weather_url, timeout=10)

        weather_data = weather_response.json()

        daily = weather_data["daily"]
        today_max = daily["temperature_2m_max"][0]
        today_min = daily["temperature_2m_min"][0]

        tomorrow_max = daily["temperature_2m_max"][1]
        tomorrow_min = daily["temperature_2m_min"][1]

        return (
          f"Today's weather in {city}: "
          f"Max {today_max}°C, Min {today_min}°C.\n"
    
          f"Tomorrow's weather in {city}: "
          f"Max {tomorrow_max}°C, Min {tomorrow_min}°C."
)


    except Exception as e:
        return f"Weather tool failed: {str(e)}"

# Tool list
tools = [get_weather]

# Create REAL agent
agent = create_react_agent(
    llm,
    tools
)

# User query
while True:

    user_input = input("\nYou: ")

    # Exit condition
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Agent: Goodbye!")
        break

    response = agent.invoke(
        {
            "messages": [
                ("human", user_input)
            ]
        }
    )

    print("\nAgent:")
    print(response["messages"][-1].content)