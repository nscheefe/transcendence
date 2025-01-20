from frontend_service.logic.gql.basics import load_query, execute_query
from .get_chat_room import getChatRoomById

def getUserChatRoomListData(request):
    """
    Fetch a list of chat room IDs for a user.
    """
    query = load_query('query/getUserChatData.gql')  # Query to fetch chatRoomsForUser
    response = execute_query(query, request)
    return response["chatRoomsForUser"]  # This returns a list of chat room dicts, e.g., [{'id': 1}, {'id': 2}]


def build_chat_room_details_query(chat_room_ids):
    """
    Dynamically build a GraphQL query to fetch detailed chat room data for each id.
    """
    # Create individual queries for each chat room and alias them
    chat_room_queries = "\n".join(
        f"""
        chatRoom{i + 1}: chatRoom(id: {chat_room_id}) {{
          ...ChatRoomDetails
        }}
        """
        for i, chat_room_id in enumerate(chat_room_ids)
    )

    # Append the fragment definition to the end of the query
    full_query = f"""
    query GetChatRoomData {{
      {chat_room_queries}
    }}

    fragment ChatRoomDetails on ChatRoomType {{
      id
      gameId
      createdAt
      name
    }}
    """
    return full_query


def getDetailedChatRoomData(request):
    """
    Fetch detailed data for each chat room for a user by:
    - Fetching chat room IDs first.
    - Dynamically building a query to resolve all details for each chat room.
    """
    # Step 1: Fetch chat room IDs using existing `getUserChatRoomListData`
    chat_rooms = getUserChatRoomListData(request)
    chat_room_ids = [room["id"] for room in chat_rooms]  # Extract IDs, e.g., [1, 2, 3]

    # Step 2: Build dynamic query to fetch detailed chat room data
    detailed_query = build_chat_room_details_query(chat_room_ids)

    # Step 3: Execute the dynamically built query and return response
    response = execute_query(detailed_query, request)

    # Parse results for each dynamically built alias
    detailed_chat_rooms = [
        response[f"chatRoom{i + 1}"] for i in range(len(chat_room_ids))
    ]
    return detailed_chat_rooms
