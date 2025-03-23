import requests
import cohere
import os
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")

# Add error checking for API key
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY not found in environment variables")

cohere_client = cohere.Client(api_key=cohere_api_key)

def fetch_data():
    """
    Fetch data from the API endpoints
    """
    try:
        base_url = 'http://localhost:5000/api'
        
        # Fetch data from all endpoints
        endpoints = {
            'financial_overview': f'{base_url}/financial_overview',
            'account_summary': f'{base_url}/account_summary'
        }
        
        data = {}
        for key, url in endpoints.items():
            try:
                response = requests.get(url)
                response.raise_for_status()
                data[key] = response.json()
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching {key}: {e}")
                data[key] = {}
        
        return data

    except Exception as e:
        logging.error(f"Error in fetch_data: {e}")
        return None

def format_data(data):
    if not data:
        return None
        
    formatted_data = f"""
    Financial Overview: {data.get('financial_overview', {})}
    Account Summary: {data.get('account_summary', {})}
    """
    return formatted_data

def get_recommendations(formatted_data):
    """
    Get recommendations from Cohere LLM
    """
    if not formatted_data:
        logging.error("No data to process")
        return None

    prompt = f"""
    Based on the following user account data, provide three personalized recommendations to help the user to save money wisely, reduce carbon emissions, and adopt eco-friendly practices.
    Do not add any other information to the response other than requested.
    Each recommendation should be 1-2 sentences long and should attempt to provide feedback in one of these categories:  
    - Transportation
    - Travel
    - Food and drinks
    - General merchandise
    - Home improvement
    - Rent and utilities
    - General services  

    Response Format Example (strictly follow this format):
    [
      {{
        "title": "Reduce Transportation Emissions",
        "description": "Switching to public transport twice a week could save you $120/month and reduce your carbon footprint by 30%.",
        "savingsAmount": "Save $120/month",
        "carbonReduction": "Reduce CO₂ by 30%",
        "category": "Transportation"
      }}
    ]

    Here is the user data:
    {formatted_data}
    
    Please ensure your response is in valid JSON format.
    """
    
    try:
        response = cohere_client.chat(
            message=prompt,
            model="command",
            temperature=0.7
        )
        
        # Access the text directly from the response
        if hasattr(response, 'text'):
            try:
                return json.loads(response.text)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse response as JSON: {e}")
                logging.info(f"Raw content: {response.text}")
                return None
        else:
            # Try accessing the response as a dictionary
            try:
                text = response.text if hasattr(response, 'text') else response.get('text', '')
                return json.loads(text)
            except (AttributeError, json.JSONDecodeError) as e:
                logging.error(f"Failed to parse response: {e}")
                logging.info(f"Full response object: {response}")
                return None
            
    except Exception as e:
        logging.error(f"Error calling Cohere API: {e}")
        logging.info(f"Full response object: {response}")
        return None