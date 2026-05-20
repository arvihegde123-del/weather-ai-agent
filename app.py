from dotenv import load_dotenv
import os
import requests
import json

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from langgraph.prebuilt import create_react_agent



# LOAD ENV VARIABLES
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")


# INITIALIZE LLM
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)


# WEATHER TOOL
@tool
def get_weather(city: str):
    """
    Get complete weather information for today and tomorrow.

    Available information:
    - max temperature
    - min temperature
    - rain probability
    - total rainfall
    - wind speed
    - UV index
    - sunrise
    - sunset

    Use all relevant weather details while answering.
    Format answers clearly in table form whenever useful.
    """

    try:

    
        #GET CITY COORDINATES
    
        geo_url = (
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={city}&count=1"
        )

        geo_response = requests.get(geo_url, timeout=10)

        geo_data = geo_response.json()

        # City validation
        if "results" not in geo_data:
            return {
                "error": f"City '{city}' not found."
            }

        latitude = geo_data["results"][0]["latitude"]
        longitude = geo_data["results"][0]["longitude"]

        
        # STEP 2 — GET WEATHER DATA
    
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"

            f"&daily="
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "rain_sum,"
            "wind_speed_10m_max,"
            "uv_index_max,"
            "sunrise,"
            "sunset"

            f"&forecast_days=2"
            f"&timezone=auto"
        )

        weather_response = requests.get(weather_url, timeout=10)

        weather_data = weather_response.json()

        daily = weather_data["daily"]

    
        # STEP 3 — STRUCTURED WEATHER REPORT
        

        weather_report = {

            "city": city,

            "today": {

                "max_temperature_c": daily["temperature_2m_max"][0],
                "min_temperature_c": daily["temperature_2m_min"][0],

                "rain_probability_percent":
                    daily["precipitation_probability_max"][0],

                "rainfall_mm":
                    daily["rain_sum"][0],

                "wind_speed_kmh":
                    daily["wind_speed_10m_max"][0],

                "uv_index":
                    daily["uv_index_max"][0],

                "sunrise":
                    daily["sunrise"][0],

                "sunset":
                    daily["sunset"][0]
            },

            "tomorrow": {

                "max_temperature_c": daily["temperature_2m_max"][1],
                "min_temperature_c": daily["temperature_2m_min"][1],

                "rain_probability_percent":
                    daily["precipitation_probability_max"][1],

                "rainfall_mm":
                    daily["rain_sum"][1],

                "wind_speed_kmh":
                    daily["wind_speed_10m_max"][1],

                "uv_index":
                    daily["uv_index_max"][1],

                "sunrise":
                    daily["sunrise"][1],

                "sunset":
                    daily["sunset"][1]
            }
        }

        return weather_report

    except Exception as e:

        return {
            "error": f"Weather tool failed: {str(e)}"
        }



# TOOL LIST


tools = [get_weather]



# CREATE AGENT

agent = create_react_agent(
    llm,
    tools
)


# CHAT LOOP

while True:

    user_input = input("\nYou: ")

    # Exit condition
    if user_input.lower() in ["exit", "quit", "bye"]:

        print("\nAgent: Goodbye!")
        break

    try:

        # INVOKE AGENT
        
        response = agent.invoke(
            {
                "messages": [
                    ("human", user_input)
                ]
            }
        )

        
        # FINAL RESPONSE
      
        final_answer = response["messages"][-1].content

        print("\nAgent:")
        print(final_answer)

    except Exception as e:

        print("\nAgent Error:")
        print(str(e))