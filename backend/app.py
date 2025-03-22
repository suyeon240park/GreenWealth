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
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

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

# Climatiq API configuration
CLIMATIQ_API_KEY = os.getenv('CLIMATIQ_API_KEY')
CLIMATIQ_BASE_URL = 'https://beta3.api.climatiq.io'

# In-memory storage for access tokens (in production, use a database)
access_tokens = {}

def map_category_to_climatiq_activity(category):
    # Map Plaid categories to Climatiq emission factors
    category_map = {
        'TRANSPORTATION': {
            'activity_id': 'passenger_vehicle-vehicle_type_car-fuel_source_na-engine_size_na-vehicle_age_na-vehicle_weight_na',
            'factor': 1.0  # Base factor for transportation
        },
        'TRAVEL': {
            'activity_id': 'passenger_flight-route_type_domestic-aircraft_type_na-distance_na-class_na',
            'factor': 1.2  # Higher impact for air travel
        },
        'FOOD_AND_DRINK': {
            'activity_id': 'meal-type_restaurant_meal',
            'factor': 0.8  # Average restaurant meal impact
        },
        'GENERAL_MERCHANDISE': {
            'activity_id': 'consumer_goods-type_clothing',
            'factor': 0.5  # General retail goods
        },
        'HOME_IMPROVEMENT': {
            'activity_id': 'construction-type_residential',
            'factor': 0.7  # Home improvement materials
        },
        'RENT_AND_UTILITIES': {
            'activity_id': 'electricity-energy_source_grid_mix',
            'factor': 0.6  # Utilities impact
        },
        'GENERAL_SERVICES': {
            'activity_id': 'office_activities-type_office_work',
            'factor': 0.3  # General services
        }
    }
    return category_map.get(category, {
        'activity_id': 'consumer_goods-type_general',
        'factor': 0.4  # Default factor
    })

async def get_emission_factors(activity_id):
    headers = {
        'Authorization': f'Bearer {CLIMATIQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f'{CLIMATIQ_BASE_URL}/emission-factors/{activity_id}',
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching emission factors: {str(e)}")
        return None

def calculate_carbon_footprint(amount, category):
    try:
        # Get the appropriate Climatiq activity mapping
        activity_mapping = map_category_to_climatiq_activity(category)
        
        # Calculate base carbon footprint using the category factor
        base_footprint = abs(float(amount)) * activity_mapping['factor']
        
        # Convert to kg CO2e
        return round(base_footprint, 2)
    except Exception as e:
        print(f"Error calculating carbon footprint: {str(e)}")
        return 0.0

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        client_id = os.getenv('PLAID_CLIENT_ID')

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
        client_id = os.getenv('PLAID_CLIENT_ID')
        
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        response = client.item_public_token_exchange(exchange_request)
        access_token = response['access_token']
        item_id = response['item_id']
        
        # Store the access token for this client
        access_tokens[client_id] = access_token
        
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
        client_id = os.getenv('PLAID_CLIENT_ID')
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            return jsonify({"error": "No access token found for client"}), 400
        
        # Set date range for transactions
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
        
        response = client.transactions_get(request)
        transactions = response['transactions']
        
        # Process transactions to match our frontend format
        processed_transactions = []
        for transaction in transactions:
            # Map Plaid categories to our carbon impact categories
            carbon_impact = map_category_to_climatiq_activity(transaction.personal_finance_category.primary)
            
            processed_transaction = {
                'id': transaction.transaction_id,
                'name': transaction.merchant_name or transaction.name,
                'amount': f"${abs(transaction.amount):.2f}",
                'date': transaction.date.strftime('%b %d, %Y'),
                'category': transaction.personal_finance_category.primary,
                'carbon': f"{calculate_carbon_footprint(transaction.amount, transaction.personal_finance_category.primary)} kg",
                'impact': carbon_impact['impact']
            }
            processed_transactions.append(processed_transaction)
        
        return jsonify(processed_transactions)
    
    except plaid.ApiException as e:
        return jsonify({"error": e.body}), 400

@app.route('/api/carbon_footprint', methods=['GET'])
def get_carbon_footprint():
    try:
        client_id = os.getenv('PLAID_CLIENT_ID')
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            return jsonify({"error": "No access token found for client"}), 400
        
        # Set date range for transactions
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
        
        response = client.transactions_get(request)
        transactions = response['transactions']
        
        # Calculate carbon footprint by category
        carbon_by_category = {}
        for transaction in transactions:
            category = transaction.personal_finance_category.primary
            carbon_impact = map_category_to_climatiq_activity(category)
            carbon_amount = calculate_carbon_footprint(transaction.amount, category)
            
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
        client_id = os.getenv('PLAID_CLIENT_ID')
        print(client_id)
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            return jsonify({"error": "No access token found for client"}), 400
        
        # Set date range for transactions (last 6 months)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        response = client.transactions_get(request)
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
        client_id = request.args.get('client_id', os.getenv('PLAID_CLIENT_ID'))
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            return jsonify({"error": "No access token found for client"}), 400
        
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
            carbon_impact = map_category_to_climatiq_activity(category)
            carbon_amount = calculate_carbon_footprint(transaction.amount, category)
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

@app.route('/api/carbon_impact_details', methods=['GET'])
def get_carbon_impact_details():
    try:
        client_id = os.getenv('PLAID_CLIENT_ID')
        access_token = access_tokens.get(client_id)
        
        if not access_token:
            return jsonify({"error": "No access token found for client"}), 400
        
        # Get transactions for the last month
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
        
        response = client.transactions_get(request)
        transactions = response['transactions']
        
        # Calculate detailed carbon impact
        impact_details = {
            'total_carbon': 0,
            'categories': {},
            'recommendations': []
        }
        
        for transaction in transactions:
            category = transaction.personal_finance_category.primary
            amount = abs(transaction.amount)
            carbon = calculate_carbon_footprint(amount, category)
            
            if category not in impact_details['categories']:
                impact_details['categories'][category] = {
                    'carbon': 0,
                    'spending': 0,
                    'transactions': 0
                }
            
            impact_details['categories'][category]['carbon'] += carbon
            impact_details['categories'][category]['spending'] += amount
            impact_details['categories'][category]['transactions'] += 1
            impact_details['total_carbon'] += carbon
        
        # Generate recommendations based on highest impact categories
        sorted_categories = sorted(
            impact_details['categories'].items(),
            key=lambda x: x[1]['carbon'],
            reverse=True
        )
        
        # TODO: Replace static recommendations with Cohere API integration
        # 1. Install cohere package: pip install cohere
        # 2. Initialize Cohere client with API key
        # 3. Use Cohere's generate endpoint to create personalized recommendations
        # 4. Consider user's spending patterns and transaction history for context
        # Example:
        # co = cohere.Client('your-api-key')
        # response = co.generate(
        #     model='command',
        #     prompt=f"Given the user's highest carbon impact category is {sorted_categories[0][0]} with {sorted_categories[0][1]['carbon']} kg CO2, suggest 3 personalized eco-friendly recommendations.",
        #     max_tokens=150,
        #     temperature=0.7
        # )
        
        recommendations = {
            'TRANSPORTATION': [
                "Consider using public transportation or carpooling",
                "Switch to an electric or hybrid vehicle",
                "Combine multiple errands into one trip"
            ],
            'FOOD_AND_DRINK': [
                "Choose more plant-based meals",
                "Buy local and seasonal produce",
                "Reduce food waste by planning meals"
            ],
            'TRAVEL': [
                "Consider virtual meetings instead of business travel",
                "Choose direct flights when possible",
                "Offset your travel emissions"
            ],
            'GENERAL_MERCHANDISE': [
                "Buy second-hand or refurbished items",
                "Choose products with minimal packaging",
                "Support eco-friendly brands"
            ]
        }
        
        # Add top 3 recommendations based on highest impact categories
        for category, _ in sorted_categories[:3]:
            if category in recommendations:
                impact_details['recommendations'].extend(recommendations[category])
        
        return jsonify(impact_details)
    
    except plaid.ApiException as e:
        return jsonify({"error": e.body}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

