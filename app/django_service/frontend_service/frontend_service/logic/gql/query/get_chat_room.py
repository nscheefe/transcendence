from frontend_service.logic.gql.basics import load_query, execute_query


def getChatRoomById(request, id):
    # Load the GraphQL query from the file
    query = load_query('query/getChatRoomData.gql')

    # Extract the ID from the request
    request.id = id

    # Execute the query with the ID variable
    response = execute_query(query, request)

    # Return the chatRoom data from the response
    return response["chatRoom"]

