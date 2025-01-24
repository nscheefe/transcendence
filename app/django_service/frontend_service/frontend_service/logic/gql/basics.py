import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def load_query(filename):
    filepath = os.path.join(os.path.dirname(__file__),  filename)
    with open(filepath, "r") as file:
        return file.read()


def execute_query(query, request, variables=None):
    headers = {"Host": "localhost:8000"}

    # Include cookies from the request
    if request:
        cookies = request.COOKIES
        cookie_header = "; ".join([f"{key}={value}" for key, value in cookies.items()])
        headers["Cookie"] = cookie_header

    transport = RequestsHTTPTransport(
        url="http://main_service:8000/graphql/",
        use_json=True,
        headers=headers,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    response = client.execute(gql(query), variable_values=variables)
    return response
