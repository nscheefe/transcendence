from frontend_service.logic.gql.basics import load_query, execute_query


def getProfileData(request, id):
    # Load the query from the file
    query = load_query('query/getProfileData.gql')

    # Define the variables for the GraphQL query
    variables = {
        "userId": id  # Pass the user ID as the variable
    }

    # Execute the query with variables
    response = execute_query(query, request, variables=variables)
    return response
