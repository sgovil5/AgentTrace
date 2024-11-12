from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from datetime import datetime
import openai
from openai import OpenAI

@dataclass
class ToolExecution:
    tool_name: str
    input_params: Dict[str, Any]
    output: Any
    timestamp: datetime

@dataclass
class MessageInfo:
    role: str
    content: str
    timestamp: datetime

@dataclass
class AgentTrace:
    conversation_id: str
    messages: List[MessageInfo]
    tool_executions: List[ToolExecution]
    start_time: datetime
    end_time: datetime
    
    def to_dict(self):
        return asdict(self)

class WeatherAgent:
    def __init__(self, openai_api_key: str, weather_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.weather_api_key = weather_api_key
        self.messages = []
        self.tool_executions = []
        self.start_time = datetime.now()
        
    # def get_weather(self, location: str) -> str:
    #     import requests
    #     from geopy.geocoders import Nominatim
        
    #     # First, convert location name to coordinates using geocoding
    #     try:
    #         geolocator = Nominatim(user_agent="weather_agent")
    #         location_data = geolocator.geocode(location)
    #         if not location_data:
    #             error_msg = f"Could not find coordinates for location: {location}"
    #             tool_execution = ToolExecution(
    #                 tool_name="weather_lookup",
    #                 input_params={"location": location},
    #                 output=error_msg,
    #                 timestamp=datetime.now()
    #             )
    #             self.tool_executions.append(tool_execution)
    #             return error_msg
            
    #         # Call OpenWeather One Call API 3.0
    #         base_url = "https://api.openweathermap.org/data/3.0/onecall"
    #         params = {
    #             "lat": location_data.latitude,
    #             "lon": location_data.longitude,
    #             "appid": self.weather_api_key,
    #             "units": "imperial",
    #             "exclude": "minutely,hourly,daily,alerts"  # Only get current weather
    #         }
            
    #         response = requests.get(base_url, params=params)
    #         response.raise_for_status()
    #         weather_data = response.json()
            
    #         # Extract current weather information
    #         current = weather_data["current"]
    #         temperature = current["temp"]
    #         condition = current["weather"][0]["main"]
            
    #         output = f"{condition}, {temperature}°F in {location}"
            
    #         # Create tool execution record
    #         tool_execution = ToolExecution(
    #             tool_name="weather_lookup",
    #             input_params={"location": location},
    #             output=output,
    #             timestamp=datetime.now()
    #         )
    #         self.tool_executions.append(tool_execution)
    #         return output
            
    #     except Exception as e:
    #         error_msg = f"Error fetching weather data: {str(e)}"
    #         tool_execution = ToolExecution(
    #             tool_name="weather_lookup",
    #             input_params={"location": location},
    #             output=error_msg,
    #             timestamp=datetime.now()
    #         )
    #         self.tool_executions.append(tool_execution)
    #         return error_msg

    def get_weather(self, location: str) -> str:
        tool_execution = ToolExecution(
            tool_name="weather_lookup",
            input_params={"location": location},
            output=f"Sunny, 72°F in {location}",
            timestamp=datetime.now()
        )
        self.tool_executions.append(tool_execution)
        return tool_execution.output

    def chat(self, user_input: str) -> str:
        # Add user message to history
        self.messages.append(MessageInfo(
            role="user",
            content=user_input,
            timestamp=datetime.now()
        ))
        
        # Define available tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]

        # Create messages for API
        api_messages = [{"role": m.role, "content": m.content} for m in self.messages]
        
        # Get response from OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Handle tool calls if any
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                if tool_call.function.name == "get_weather":
                    location = eval(tool_call.function.arguments)["location"]
                    weather_info = self.get_weather(location)
                    
                    # Add tool response to messages
                    self.messages.append(MessageInfo(
                        role="assistant",
                        content=f"I looked up the weather: {weather_info}",
                        timestamp=datetime.now()
                    ))
        else:
            # Add regular assistant response to messages
            self.messages.append(MessageInfo(
                role="assistant",
                content=assistant_message.content,
                timestamp=datetime.now()
            ))
            
        return self.messages[-1].content

    def get_trace(self) -> AgentTrace:
        return AgentTrace(
            conversation_id=str(datetime.now().timestamp()),
            messages=self.messages,
            tool_executions=self.tool_executions,
            start_time=self.start_time,
            end_time=datetime.now()
        )