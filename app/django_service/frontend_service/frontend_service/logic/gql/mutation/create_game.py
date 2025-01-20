from frontend_service.logic.gql.basics import load_query, execute_query

def createGame(request):
    """
    Creates a new game or returns an existing unfinished Game by executing a GraphQL mutation.

    Args:
        request: The request object containing the necessary data to create a game.

    Returns:
        dict: The game object returned from the GraphQL response.
    """
    query = load_query('mutation/createGame.gql')
    response = execute_query(query, request)
    return response

