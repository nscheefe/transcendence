from .gql.query.get_user_data import getUserProfileData


def get_home_context(request):
    user_data = getUserProfileData(request)
    context = {
        'show_nav': True,
        'user_name': request.user.username,  # Example: passing the username
        'user': user_data,
    }
    return context
