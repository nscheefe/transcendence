from math import e
from venv import logger
from frontend_service.logic.gql.basics import load_query, execute_query

def manageProfile(request, bio=None, nickname=None, avatarPath=None, additionalInfo=None):
    logger.info("Updating profile with bio: %s, nickname: %s, avatarPath: %s, additionalInfo: %s", bio, nickname, avatarPath, additionalInfo)
    query = load_query("mutation/updateProfile.gql")
    variables = {}
    if bio is not None:
        variables["bio"] = bio
    if nickname is not None:
        variables["nickname"] = nickname
    if avatarPath:
        variables["avatarUrl"] = avatarPath
    if additionalInfo is not None:
        variables["additionalInfo"] = additionalInfo
    response = execute_query(query, request, variables)
    return response['manageProfile']
