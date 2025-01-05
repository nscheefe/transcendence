from frontend_service.logic.query.basics import load_query, execute_query

def getUserProfileData(request):
    query = load_query('getUserData.gql')

    response = execute_query(query, request)
    return response["user"]


