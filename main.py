from agent_info import WeatherAgent
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

def run_agent():
    username = quote_plus(os.getenv('MONGO_USERNAME'))
    password = quote_plus(os.getenv('MONGO_PASSWORD'))
    mongo_uri = f"mongodb+srv://{username}:{password}@cluster0.u87uqzy.mongodb.net/"

    # Connect to MongoDB Atlas
    mongo_client = MongoClient(mongo_uri)
    try:
        db = mongo_client['AgentTrace'] 
        traces_collection = db['Runs']   

        # Initialize the agent
        agent = WeatherAgent(openai_api_key=OPENAI_API_KEY, weather_api_key=WEATHER_API_KEY)
        
        # Have a conversation
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
                
            response = agent.chat(user_input)
            print(f"Agent: {response}")
        
        # Get and store the trace
        trace = agent.get_trace()
        traces_collection.insert_one(trace.to_dict())
        print("\nConversation trace stored in MongoDB Atlas!")

    finally:
        # Properly close the MongoDB connection
        mongo_client.close()

if __name__ == "__main__":
    run_agent()