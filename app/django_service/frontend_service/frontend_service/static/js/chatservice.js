import { executeSubscription, executeMutation, executeQuery, } from "./utils.js"

export const startChatWithUser = async (userId, gameId = null) => {
    const mutation = `
    mutation StartChatWithUser($userId: Int!, $gameId: Int) {
        startChatWithUser(user_id: $userId, game_id: $gameId) {
            id
            name
            created_at
            game_id
            users {
                id
                user_id
                chat_room_id
                joined_at
            }
        }
    }
    `;
    const variables = { userId: parseInt(userId, 10), gameId: gameId };
    return executeMutation(mutation, variables);
};

/**
 * Subscribes to real-time updates for the user's chat rooms.
 * @param {function} onChatRoomUpdate - Callback function, triggered on receiving a new update.
 * @param {function} [onError] - Callback function, triggered on error during the subscription.
 * @returns {function} - A function to unsubscribe from the subscription.
 */
export const subscribeToUserChatRooms = (onChatRoomUpdate, onError) => {
    const subscriptionQuery = {
        query: `
        subscription ChatRoomUpdates {
            chatRoomsForUser {
                id,
                name
                users {
                    id
                    user_id
                    chat_room_id
                    joined_at
                }
            }
        }
        `,
        variables: {},
        extensions: {},
        operationName: "ChatRoomUpdates",
    };
    executeSubscription(subscriptionQuery, onChatRoomUpdate, onError,);
};


export const subscribeToChatRoomMessages = (chatRoomId, onMessageUpdate, onError) => {
    const subscriptionQuery = {
        query: `
        subscription Chat_room_message($id: Int!) {
            chat_room_message(chat_room_id: $id) {
                id
                content
                sender_id
                chat_room_id
                timestamp
            }
        }
        `,
        variables: { id: chatRoomId },
        extensions: {},
        operationName: "Chat_room_message",
    };
    executeSubscription(subscriptionQuery, onMessageUpdate, onError);
};

export const sendChatRoomMessage = async (chatRoomId, content, senderId) => {
    const mutation = `
    mutation Create_chat_room_message($id: Int!, $content: String!) {
        create_chat_room_message(
            chat_room_id: $id,
            content: $content
        ) {
            id
            content
            sender_id
            chat_room_id
            timestamp
        }
    }
    `;
    const variables = { id: parseInt(chatRoomId, 10), content: content };
    return executeMutation(mutation, variables);
};


export const fetchUserDetails = async (userId) => {
    const query = `
    query Profile($userId: Int!) {
        profile(userId: $userId) {
            nickname
            avatarUrl
            userId
        }
    }
    `;
    const variables = { userId: parseInt(userId, 10) };
    return executeQuery(query, variables);
};



export const fetchChatRoomMessages = async (chatRoomId) => {
    const query = `
        query {
            chatRoom(id: ${chatRoomId}) {
                messages {
                    chatRoomId
                    content
                    senderId
                    id
                    timestamp
                }
            }
        }
    `;
    return executeQuery(query);
};

/**
 * Dynamically builds a query for fetching chat room details for multiple IDs.
 * @param {Array<number>} ids - Array of chat room IDs.
 * @returns {string} A GraphQL query string to fetch chat room details.
 */
export const buildChatRoomDetailsQuery = (ids) => {
    if (!Array.isArray(ids) || ids.length === 0) {
        throw new Error("Empty or invalid 'ids' array provided.");
    }
    const sanitizedIds = ids.filter((id) => typeof id === 'number' && Number.isFinite(id));
    if (sanitizedIds.length === 0) {
        throw new Error("No valid chat room IDs available.");
    }

    let queryBody = '';
    for (let i = 0; i < sanitizedIds.length; i++) {
        queryBody += `chatRoom${i + 1}: chatRoom(id: ${sanitizedIds[i]}) { id name users { userId } }\n`;
    }

    return `
        query {
            ${queryBody}
        }
    `;
};

/**
 * Fetches details for each given chat room ID.
 * @param {Array<number>} ids - List of chat room IDs.
 * @returns {Promise<Array>} The details of the user chat rooms.
 */
export const fetchChatRoomDetails = async (ids) => {
    const query = buildChatRoomDetailsQuery(ids);
    const data = await fetchGraphQL(query);
    return ids.map((id, index) => data[`chatRoom${index + 1}`]);
};

/**
 * Removes the current user from a specified chat room.
 * @param {number} chatRoomId - The ID of the chat room.
 * @returns {Promise<Object>} The response from the GraphQL server.
 */
export const removeUserFromChatRoom = async (chatRoomId) => {
    const mutation = `
    mutation RemoveUserFromChatRoom($chatRoomId: Int!) {
        remove_user_from_chat_room(chat_room_id: $chatRoomId) {
            id
            user_id
            chat_room_id
            removed_at
        }
    }
    `;
    const variables = {
        chatRoomId: parseInt(chatRoomId, 10), // Ensure the ID is an integer
    };
    return executeMutation(mutation, variables);
};

export const declineGameInvitation = async (gameId) => {
    const mutation = `
    mutation Update_game_state($gameId: Int!, $state: String!) {
        update_game_state(game_id: $gameId, state: $state) {
            id
            state
            points_player_a
            points_player_b
            player_a_id
            player_b_id
            finished
            created_at
            updated_at
            }
        }
    `;
    const variables = { gameId: parseInt(gameId, 10), state: "DECLINED" };
    return executeMutation(mutation, variables);
};

