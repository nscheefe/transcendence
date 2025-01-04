from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def getUserProfileData(request):
	transport = RequestsHTTPTransport(
		url='http://main_service:8000/graphql/',
		use_json=True,
		headers={
			'Host': 'localhost:8000'
		}
	)
	client = Client(transport=transport, fetch_schema_from_transport=False)

	query = gql("""
	query GetUserProfileData {
	  getUserProfileData {
		username
		email
		profilePic
		bio
		location
		website
	  }
	}
	""")
	response = client.execute(query)
	return response['getUserProfileData']
