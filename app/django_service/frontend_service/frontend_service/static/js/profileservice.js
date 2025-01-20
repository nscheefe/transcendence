import {fetchGraphQL} from './utils.js';

/**
 * Fetches the user's profile and stats.
 * @param {number} userId - The user's ID.
 * @returns {Promise<object>} The user's profile and stats.
 */
export const fetchUserProfileAndStats = async (userId) => {
    const query = `
        query {
            user {
                profile {
                    avatarUrl
                    additionalInfo
                    bio
                    nickname
                    userId
                }
                createdAt
                name
                mail
            }
            calculateUserStats(userId: ${Number(userId)}) {
                totalGames
                totalWins
                totalLosses
            }
        }
    `;
    return fetchGraphQL(query);
};

/**
 * Fetches all profiles with pagination support.
 * @param {number} limit - The maximum number of profiles to fetch.
 * @param {number} offset - The offset for pagination.
 * @returns {Promise<object>} The paginated list of profiles.
 */
export const fetchProfiles = async (limit, offset) => {
    const query = `
        query {
            getAllProfiles(limit: ${limit}, offset: ${offset}) {
                profiles {
                    additionalInfo
                    avatarUrl
                    bio
                    nickname
                    userId
                }
            }
        }
    `;
    return fetchGraphQL(query);
};