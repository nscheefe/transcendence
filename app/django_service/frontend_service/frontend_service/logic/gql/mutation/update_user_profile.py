from frontend_service.logic.gql.basics import load_query, execute_query

def update_user_profile(user, bio, nickname, avatar_path=None):
    # Update the user profile with the provided data
    user.profile.bio = bio
    user.profile.nickname = nickname
    if avatar_path:
        user.profile.avatar_url = avatar_path
    user.profile.save()
