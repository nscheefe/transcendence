import uuid
import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def signIn(request):
    # Generate a unique state key
    state_key = str(uuid.uuid4())

    # Construct the OAuth URL
    client_id = os.getenv('CLIENT_ID')
    redirect_uri = os.getenv('REDIRECT_URI')
    oauth_url = (
        f"https://api.intra.42.fr/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&state={state_key}"
    )

    context = {
        'oauth_url': oauth_url
    }
    return context

def exchange_code_for_token(code, state):
    transport = RequestsHTTPTransport(
        url='http://main_service:8000/auth/',
        use_json=True,
        headers={
            'Host': 'localhost:8000'
        }
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql("""
    mutation ExchangeCodeForToken($input: ExchangeCodeForTokenInput!) {
      exchangeCodeForToken(input: $input) {
        jwtToken
      }
    }
    """)
    variables = {
        "input": {
            "code": code,
            "state": state
        }
    }
    response = client.execute(query, variable_values=variables)
    return response
