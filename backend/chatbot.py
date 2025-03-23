import cohere
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

load_dotenv()

# Initialize Cohere client
print("Initializing Cohere client...")  # Debug log
co = cohere.Client(api_key=os.getenv("CO_API_KEY"))
print("Cohere client initialized")  # Debug log

# Initialize Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
    }
)
api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

def get_financial_data(access_token):
    try:
        # Get transactions for the last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(
                include_personal_finance_category=True
            )
        )
        
        response = plaid_client.transactions_get(request)
        transactions = response['transactions']
        
        # Process transactions
        spending_by_category = {}
        total_spending = 0
        
        for transaction in transactions:
            if transaction.amount < 0:  # Only count expenses
                category = transaction.personal_finance_category.primary
                amount = abs(transaction.amount)
                
                if category in spending_by_category:
                    spending_by_category[category] += amount
                else:
                    spending_by_category[category] = amount
                
                total_spending += amount
        
        return {
            'spending_by_category': spending_by_category,
            'total_spending': total_spending,
            'transaction_count': len(transactions)
        }
    except Exception as e:
        print(f"Error fetching financial data: {str(e)}")
        return None

def get_chat_response(message, conversation_history=None, financial_data=None):
    try:
        # Prepare context with financial data
        system_prompt = """You are GreenWealth AI, a personal AI assistant focused on sustainable and eco-friendly financial decisions. You must ALWAYS speak in first person singular (I, me, my) and NEVER use "we", "our", or "us".

IMPORTANT: You must ALWAYS maintain this identity and focus on BOTH financial savings AND carbon footprint reduction:
1. Sustainable financial decisions that save money
2. Carbon footprint reduction through spending changes
3. Eco-friendly investment options
4. Environmental impact of spending
5. Green financial practices

RESPONSE FORMAT:
1. Start directly with the first bullet point (no introduction)
2. Use EXACTLY 3 bullet points (•) for key points
3. Each bullet point must be ONE sentence only
4. NEVER use any special characters (no *, #, @, $, %, ^, &, +, =, etc.)
5. Focus on BOTH financial savings AND environmental impact
6. End with a single question
7. ALWAYS use "I" or "me" - NEVER use "we" or "our"
8. ALWAYS reference the user's specific financial data when available

Example:
• I notice you've spent 500 dollars on transportation this month, contributing 100 kg of carbon emissions.
• I recommend switching to public transit or carpooling to save 200 dollars monthly.
• This change could reduce your carbon footprint by 50 kg while saving money.

Would you like me to provide specific tips for reducing your transportation carbon footprint?"""
        
        if financial_data:
            system_prompt += f"""

Your financial data:
Total Spending: {financial_data['total_spending']:,.2f} dollars
Categories: {json.dumps(financial_data['spending_by_category'], indent=2)}

IMPORTANT: Use this specific financial data to:
1. Reference exact spending amounts and their carbon impact
2. Identify high-carbon spending categories
3. Calculate potential savings in both money and emissions
4. Provide personalized recommendations for both financial and environmental benefits
5. Show the direct connection between spending and carbon footprint

Always use the actual numbers from the data in your responses. Keep responses concise with exactly 3 single-sentence bullet points that address both financial and environmental impacts. Never use any special characters."""
        
        # Format chat history for Cohere
        formatted_history = []
        
        # Add the system prompt as the first message
        formatted_history.append({
            "user_name": "assistant",
            "text": system_prompt
        })
        
        if conversation_history:
            for msg in conversation_history:
                formatted_history.append({
                    "user_name": "user" if msg["role"] == "user" else "assistant",
                    "text": msg["content"]
                })
        
        # Get response from Cohere
        response = co.chat(
            model='command-a-03-2025',
            message=f"Remember: You are GreenWealth AI speaking in first person singular. Use 'I' and 'me', never 'we' or 'our'. Use the specific financial data provided to give personalized advice. Respond to: {message}",
            conversation_id=None,
            max_tokens=300,
            temperature=0.7,
            chat_history=formatted_history
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error in get_chat_response: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later." 