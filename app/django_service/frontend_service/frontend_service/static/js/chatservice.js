import {fetchGraphQL} from './utils.js';

/**
 * Fetches chat room messages by ID.
 * @param {number} chatRoomId - The ID of the chat room.
 * @returns {Promise<Array>} The list of messages.
 */
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
    return fetchGraphQL(query);
};

/**
 * Fetches the list of all chat rooms for a user.
 * @returns {Promise<Array>} The list of chat rooms.
 */
export const fetchUserChatRooms = async () => {
    const query = `
        query {
            chatRoomsForUser {
                id
            }
        }
    `;
    return fetchGraphQL(query);
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