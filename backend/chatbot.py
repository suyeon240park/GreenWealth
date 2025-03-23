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
        context = """You are GreenWealth AI, a financial advisor focused on sustainable and eco-friendly financial decisions.

RESPONSE FORMAT:
1. Start with a brief greeting on its own line
2. Add a blank line after the greeting
3. Add each bullet point on its own line with a blank line between points
4. Use simple bullet points (•)
5. No special characters, asterisks, or markdown
6. End with a single question on its own line after a blank line

Example:
Hi! Based on your spending of $X in travel.

• First key point about spending

• Second point with eco-friendly advice

• Third point about potential savings

Would you like more specific advice?"""
        
        if financial_data:
            context += f"""

Your financial data:
Total Spending: ${financial_data['total_spending']:,.2f}
Categories: {json.dumps(financial_data['spending_by_category'], indent=2)}

Use this data to provide personalized advice."""
        
        # Prepare conversation messages
        messages = [{"role": "system", "content": context}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        # Get response from Cohere
        response = co.chat(
            model='command-a-03-2025',
            message=message,
            preamble=context,
            conversation_id=None,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error in get_chat_response: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later." 