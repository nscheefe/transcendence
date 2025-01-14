const graphqlEndpoint = '/graphql/';

/**
 * Sends a GraphQL query request.
 * @param {string} query - The GraphQL query string.
 * @returns {Promise<object>} - The resulting data from the query.
 */
const fetchGraphQL = async (query) => {
    try {
        const response = await fetch(graphqlEndpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query}),
            credentials: 'include'
        });

        const {data, errors} = await response.json();
        if (errors) throw new Error(errors[0]?.message || 'GraphQL Errors');
        return data;
    } catch (error) {
        console.error('GraphQL error:', error);
        throw error;
    }
};

/**
 * Fetches friendships for the logged-in user.
 * @returns {Promise<array>} - Array of friendship objects.
 */
export const fetchFriendships = async () => {
    const friendshipsQuery = `
        query GetFriendships {
            user {
                friendships {
                    friendId
                    accepted
                    establishedAt
                    userId
                }
            }
        }
    `;

    try {
        const {user} = await fetchGraphQL(friendshipsQuery);
        return user.friendships || [];
    } catch (error) {
        console.error('Failed to fetch friendships:', error);
        throw error;
    }
};

/**
 * Dynamically generates a GraphQL query to fetch profiles for each friend ID.
 * @param {array} friendships - Array of friendship objects.
 * @returns {string} - The combined GraphQL query for fetching profiles.
 */
const buildProfileQuery = (friendships) => {
    return friendships
        .map((friendship, index) => `
            friend${index}: profile(userId: ${friendship.friendId}) {
                additionalInfo
                avatarUrl
                nickname
                bio
                userId
            }
        `)
        .join('\n');
};

/**
 * Fetches friendships and associated profiles in one combined query.
 * @param {array} friendships - Array of friendship objects.
 * @returns {Promise<object>} - Combined friendships and profiles data.
 */
export const fetchFriendsWithProfiles = async (friendships) => {
    const profileQueries = buildProfileQuery(friendships);

    const combinedQuery = `
        query GetFriendshipsAndProfiles {
            friendships: user {
                friendships {
                    friendId
                    accepted
                    establishedAt
                    userId
                }
            }

            ${profileQueries}
        }
    `;

    try {
        return await fetchGraphQL(combinedQuery);
    } catch (error) {
        console.error('Failed to fetch friends and their profiles:', error);
        throw error;
    }
};