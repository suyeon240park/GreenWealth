from flask import Flask, request, jsonify
from flask_cors import CORS
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
from plaid.model.depository_filter import DepositoryFilter
from plaid.model.depository_account_subtypes import DepositoryAccountSubtypes
from plaid.model.depository_account_subtype import DepositoryAccountSubtype
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.accounts_get_request import AccountsGetRequest
import random
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
from chatbot import get_chat_response
import requests
from cohere_insights import get_recommendations, format_data, fetch_data

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# In-memory storage for access tokens (in production, use a database)
access_tokens = {}

# Store conversation history
conversation_history = {}

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        data = request.get_json()
        client_id = data.get('clientId') or os.getenv('PLAID_CLIENT_ID')

        # Create a link token with more specific configurations
        link_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=client_id
            ),
            client_name="EcoFinance App",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
            account_filters=LinkTokenAccountFilters(
                depository=DepositoryFilter(
                    account_subtypes=DepositoryAccountSubtypes([
                        DepositoryAccountSubtype("checking"),
                        DepositoryAccountSubtype("savings")
                    ])
                )
            )
        )
        
        response = client.link_token_create(link_request)
        
        # Extract link_token specifically
        link_token = response['link_token']
        return jsonify({
            'link_token': link_token,
            'expiration': response['expiration']
        })
    
    except plaid.ApiException as e:
        print(f"Plaid API error: {e.body}")
        return jsonify({"error": e.body}), 400
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    try:
        request_data = request.get_json()
        public_token = request_data.get('public_token')
        client_id = request_data.get('client_id')
        
        if not client_id:
            print("No client_id provided in request")  # Debug log
            return jsonify({"error": "client_id is required"}), 400
            
        print(f"Exchanging public token for client {client_id}")  # Debug log
        print(f"Current access tokens: {access_tokens}")  # Debug log
        
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        response = client.item_public_token_exchange(exchange_request)
        access_token = response['access_token']
        item_id = response['item_id']
        
        # Store the access token for this client
        access_tokens[client_id] = access_token
        print(f"Stored access token for client {client_id}")  # Debug log
        print(f"Updated access tokens: {access_tokens}")  # Debug log
        
        return jsonify({
            'access_token': access_token,
            'item_id': item_id,
            'client_id': client_id
        })
    
    except plaid.ApiException as e:
        return jsonify({"error": e.body}), 400

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        client_id = request.args.get('client_id', 'default')
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            # Return empty list if no bank connected
            return jsonify([])
        
        # Set date range for transactions
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        plaid_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(
                include_personal_finance_category=True
            )
        )
        
        response = client.transactions_get(plaid_request)
        transactions = response['transactions']
        
        # Process transactions to match frontend format
        processed_transactions = []
        for transaction in transactions:
            # Map Plaid categories to our carbon impact categories
            carbon_impact = map_category_to_carbon_impact(transaction.personal_finance_category.primary)
            
            processed_transaction = {
                'id': transaction.transaction_id,
                'name': transaction.merchant_name or transaction.name,
                'amount': f"${abs(transaction.amount):.2f}",
                'date': transaction.date.strftime('%b %d, %Y'),
                'category': transaction.personal_finance_category.primary,
                'carbon': f"{calculate_carbon_footprint(transaction.amount, carbon_impact['factor'])} kg",
                'impact': carbon_impact['impact']
            }
            processed_transactions.append(processed_transaction)
        
        return jsonify(processed_transactions)
    
    except plaid.ApiException as e:
        return jsonify({"error": e.body}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def map_category_to_carbon_impact(category):
    # Find them from API doc
    category_map = {
        # using GHG Protocol coefficient for estimation for transportation
        'TRANSPORTATION': {'impact': 'high', 'factor': 1.853},
        # using U.S. Government (EPA) coefficient fo estimation for travel
        'TRAVEL': {'impact': 'high', 'factor': 1.278},
        # using  U.S. Government (EPA) coefficient calc for estimation for food
        'FOOD_AND_DRINK': {'impact': 'medium', 'factor': 0.255}, #
        # using U.S. Government (EPA) coefficient for estimation for general merchandise
        'GENERAL_MERCHANDISE': {'impact': 'medium', 'factor': 0.194},
        # using U.S. Government (EPA) coefficient fo estimation for home improvement
        'HOME_IMPROVEMENT': {'impact': 'medium', 'factor': 0.2678},
        # using U.S. Government (EPA) coefficient fo estimation for rent and utilities
        'RENT_AND_UTILITIES': {'impact': 'medium', 'factor': 0.1211},
        # using U.S. Government (EPA) coefficient fo estimation for general services
        'GENERAL_SERVICES': {'impact': 'low', 'factor': 0.1417},
    }
    
    return category_map.get(category, {'impact': 'low', 'factor': 0.05})

# Modify them later
def calculate_carbon_footprint(amount, factor):
    return round(abs(float(amount)) * factor, 1)

@app.route('/api/carbon_footprint', methods=['GET'])
def get_carbon_footprint():
    try:
        client_id = request.args.get('client_id', 'default')
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            # Return empty data if no bank connected
            return jsonify([])
        
        # Set date range for transactions
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        plaid_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(
                include_personal_finance_category=True
            )
        )
        
        response = client.transactions_get(plaid_request)
        transactions = response['transactions']
        
        # Calculate carbon footprint by category
        carbon_by_category = {}
        for transaction in transactions:
            # Skip non-carbon-emitting categories
            category = transaction.personal_finance_category.primary
            if category in ['INCOME', 'LOAN_PAYMENTS', 'TRANSFER_IN', 'TRANSFER_OUT']:
                continue
                
            carbon_impact = map_category_to_carbon_impact(category)
            carbon_amount = calculate_carbon_footprint(transaction.amount, carbon_impact['factor'])
            
            if category in carbon_by_category:
                carbon_by_category[category] += carbon_amount
            else:
                carbon_by_category[category] = carbon_amount
        
        # Format for pie chart
        carbon_data = []
        colors = {
            'TRANSPORTATION': '#ef4444',
            'FOOD_AND_DRINK': '#f97316',
            'RENT_AND_UTILITIES': '#3b82f6',
            'GENERAL_MERCHANDISE': '#8b5cf6',
            'GENERAL_SERVICES': '#10b981',
            'TRAVEL': '#ec4899',
            'HOME_IMPROVEMENT': '#14b8a6'
        }
        
        for category, value in carbon_by_category.items():
            display_name = category.replace('_', ' ').title()
            carbon_data.append({
                'name': display_name,
                'value': round(value / 1000, 1),  # Convert to tons
                'color': colors.get(category, '#6b7280')
            })
        
        return jsonify(carbon_data)
    
    except plaid.ApiException as e:
        return jsonify({"error": e.body}), 400

@app.route('/api/financial_overview', methods=['GET'])
def get_financial_overview():
    try:
        client_id = request.args.get('client_id', 'default')
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            # Return empty data if no bank connected
            return jsonify([])
        
        # Set date range for transactions (last 6 months)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        
        plaid_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        response = client.transactions_get(plaid_request)
        transactions = response['transactions']
        
        # Group transactions by month
        months = {}
        for transaction in transactions:
            month = transaction.date.strftime('%b')
            amount = abs(transaction.amount)
            
            if month not in months:
                months[month] = {'Spending': 0, 'Income': 0}
            
            # Negative amounts are expenses, positive are income in Plaid
            if transaction.amount < 0:
                months[month]['Spending'] += amount
            else:
                months[month]['Income'] += amount
        
        # Calculate savings (Income - Spending)
        for month in months:
            months[month]['Saving'] = max(0, months[month]['Income'] - months[month]['Spending'])
        
        # Format for chart
        overview_data = []
        for month, data in months.items():
            overview_data.append({
                'name': month,
                'Spending': round(data['Spending'], 2),
                'Saving': round(data['Saving'], 2),
                'Income': round(data['Income'], 2)
            })
        
        # Sort by month
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        overview_data.sort(key=lambda x: month_order.index(x['name']))
        
        # Take only the last 6 months
        overview_data = overview_data[-6:]
        
        return jsonify(overview_data)
    
    except plaid.ApiException as e:
        return jsonify({"error": e.body}), 400


@app.route('/api/account_summary', methods=['GET'])
def get_account_summary():
    try:
        client_id = request.args.get('client_id', 'default')
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            # Return default data if no bank connected
            return jsonify({
                "totalBalance": "$0.00",
                "monthlySpending": "$0.00",
                "carbonFootprint": "0 tons CO₂",
                "balanceChange": "0%",
                "spendingChange": "0%",
                "carbonChange": "0%"
            })
        
        # Get account balances
        accounts_request = AccountsGetRequest(access_token=access_token)
        accounts_response = client.accounts_get(accounts_request)
        accounts = accounts_response['accounts']
        
        # Calculate total balance from all accounts
        total_balance = sum(account.balances.current for account in accounts)
        
        # Get transactions for the last month to calculate spending
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        transactions_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(
                include_personal_finance_category=True
            )
        )
        
        transactions_response = client.transactions_get(transactions_request)
        transactions = transactions_response['transactions']
        
        # Calculate monthly spending (negative transactions)
        monthly_spending = sum(abs(transaction.amount) for transaction in transactions if transaction.amount < 0)
        
        # Calculate carbon footprint based on transactions
        carbon_footprint = 0
        for transaction in transactions:
            category = transaction.personal_finance_category.primary
            carbon_impact = map_category_to_carbon_impact(category)
            carbon_amount = calculate_carbon_footprint(transaction.amount, carbon_impact['factor'])
            carbon_footprint += carbon_amount
        
        # Convert to tons
        carbon_footprint = round(carbon_footprint / 1000, 1)
        
        # Generate mock changes (in a real app, you would compare with previous periods)
        balance_change = round(random.uniform(1.0, 3.5), 1)
        spending_change = round(random.uniform(-5.0, -2.0), 1)
        carbon_change = round(random.uniform(-15.0, -8.0), 1)
        
        summary = {
            "totalBalance": f"${total_balance:,.2f}",
            "monthlySpending": f"${monthly_spending:,.2f}",
            "carbonFootprint": f"{carbon_footprint} tons CO₂",
            "balanceChange": f"+{balance_change}%",
            "spendingChange": f"{spending_change}%",
            "carbonChange": f"{carbon_change}%"
        }
        
        return jsonify(summary)
    
    except plaid.ApiException as e:
        return jsonify({"error": e.body}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-insights', methods=['GET'])
def get_ai_insights():
    try:
        data = fetch_data()
        formatted_data = format_data(data)
        recommendations = get_recommendations(formatted_data)
        if not recommendations:
            return jsonify([])
        return jsonify(recommendations)
    except Exception as e:
        print(f"Error generating AI insights: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        print("Received chat request")  # Debug log
        data = request.get_json()
        print(f"Request data: {data}")  # Debug log
        
        message = data.get('message')
        user_id = data.get('user_id', 'default')
        
        if not message:
            print("No message provided")  # Debug log
            return jsonify({"error": "Message is required"}), 400
        
        print(f"Processing message for user {user_id}: {message}")  # Debug log
        print(f"Available access tokens: {access_tokens}")  # Debug log
        
        # Get or initialize conversation history for this user
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        # Get access token for the user
        access_token = access_tokens.get(user_id)
        print(f"Access token for user {user_id}: {access_token}")  # Debug log
        
        # Get financial data if access token exists
        financial_data = None
        if access_token:
            try:
                # Get transactions for the last 30 days
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)
                
                plaid_request = TransactionsGetRequest(
                    access_token=access_token,
                    start_date=start_date,
                    end_date=end_date,
                    options=TransactionsGetRequestOptions(
                        include_personal_finance_category=True
                    )
                )
                
                response = client.transactions_get(plaid_request)
                transactions = response['transactions']
                print(f"Retrieved {len(transactions)} transactions")  # Debug log
                
                # Process transactions
                spending_by_category = {}
                total_spending = 0
                carbon_by_category = {}
                total_carbon = 0
                total_income = 0
                
                for transaction in transactions:
                    if transaction.amount < 0:  # Expenses
                        category = transaction.personal_finance_category.primary
                        amount = abs(transaction.amount)
                        
                        # Calculate spending by category
                        if category in spending_by_category:
                            spending_by_category[category] += amount
                        else:
                            spending_by_category[category] = amount
                        
                        total_spending += amount
                        
                        # Calculate carbon impact
                        carbon_impact = map_category_to_carbon_impact(category)
                        carbon_amount = calculate_carbon_footprint(transaction.amount, carbon_impact['factor'])
                        
                        if category in carbon_by_category:
                            carbon_by_category[category] += carbon_amount
                        else:
                            carbon_by_category[category] = carbon_amount
                        
                        total_carbon += carbon_amount
                    else:  # Income
                        total_income += transaction.amount
                
                financial_data = {
                    'spending_by_category': spending_by_category,
                    'total_spending': total_spending,
                    'carbon_by_category': carbon_by_category,
                    'total_carbon': total_carbon,
                    'total_income': total_income,
                    'transaction_count': len(transactions)
                }
                print(f"Fetched financial data: {financial_data}")  # Debug log
            except Exception as e:
                print(f"Error fetching financial data: {str(e)}")
                print(f"Access token: {access_token}")  # Debug log
                print(f"User ID: {user_id}")  # Debug log
                import traceback
                print(f"Traceback: {traceback.format_exc()}")  # Debug log
        else:
            print(f"No access token found for user {user_id}")  # Debug log
            print(f"Available access tokens: {access_tokens}")  # Debug log
        
        # Get response from chatbot
        print("Getting response from chatbot...")  # Debug log
        response = get_chat_response(message, conversation_history[user_id], financial_data)
        print(f"Chatbot response: {response}")  # Debug log
        
        # Update conversation history
        conversation_history[user_id].append({"role": "user", "content": message})
        conversation_history[user_id].append({"role": "assistant", "content": response})
        
        # Keep only the last 10 messages to prevent context from getting too long
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]
        
        return jsonify({
            "response": response,
            "conversation_history": conversation_history[user_id]
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")  # Debug log
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)

