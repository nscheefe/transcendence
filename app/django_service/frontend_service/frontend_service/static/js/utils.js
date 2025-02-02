import { SubscriptionClient } from 'https://cdn.jsdelivr.net/npm/@httptoolkit/subscriptions-transport-ws@0.11.2/+esm';
import { subscribeToOnlineStatus } from './notificationService.js';

import { fetchUserDetails } from './chatservice.js';

// utils.js
import { parse } from "https://cdn.jsdelivr.net/npm/graphql@15.8.0/+esm";
const protocol = window.location.protocol === "https:" ? "https:" : "http:";
const wsProtocol = protocol === "https:" ? "wss:" : "ws:";
const host = window.location.host;
const httpUrl = `${protocol}//${host}/graphql/`;
const wsUrl = `${wsProtocol}//${host}/graphql/`;

const userCache = {}; // Cache to store user details
const subscribedUsers = new Set(); // Track subscribed users

const wsClient = new SubscriptionClient(wsUrl, {
  reconnect: true,
});

/**
 * Executes a query using the HTTP client.
 * @param {Object} query - GraphQL query.
 * @param {Object} variables - GraphQL query variables.
 * @returns {Promise<Object>} - Query result.
 */
export async function executeQuery(query, variables = {}) {
  const response = await fetch(httpUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  const result = await response.json();
  if (result.errors) {
      showToast("[DEBUG] GraphQL errors:", result.errors);
  }
  return result.data;
}

/**
 * Executes a mutation using the HTTP client.
 * @param {string} mutation - GraphQL mutation.
 * @param {Object} [variables] - Variables for the mutation (optional).
 * @returns {Promise<Object>} - Mutation result.
 */
export async function executeMutation(mutation, variables = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };

    const body = JSON.stringify({
        query: mutation,
        variables: variables,
    });


    try {
        const response = await fetch(httpUrl, {
            method: 'POST',
            headers: headers,
            body: body,
        });

        if (!response.ok) {
            const errorText = await response.text();
            showToast("[DEBUG] HTTP Error Response:", errorText); // Log the error response
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.errors) {
            showToast("[DEBUG] GraphQL errors:", result.errors);
        }
        return result.data;
    } catch (error) {
        showToast("[DEBUG] Mutation Error:", error);
        throw error;
    }
}

/**
 * Executes a subscription using the WebSocket client.
 * @param {Object|string} subscriptionQuery - A raw query string with variables or parsed query object.
 * @param {Function} [onNext] - Callback to handle subscription updates.
 * @param {Function} [onError] - Callback to handle subscription errors.
 * @param onComplete
 */
export function executeSubscription(
  subscriptionQuery,
  onNext = (data) => console.log("[DEBUG] Subscription Data Received:", data),
  onError = (error) => console.error("[DEBUG] Subscription Error:", error),
  onComplete = () => console.log("[DEBUG] Subscription Complete.")
) {


    const subscription = wsClient.request(subscriptionQuery).subscribe({
      next: onNext,
      error: onError,
      complete: onComplete,
    });
}



/**
 * Adds an error message to a container for display.
 * @param {HTMLElement} container - The DOM container to append the error message.
 * @param {string} errorMessage - The error message to display.
 */
export const showError = (container, errorMessage) => {
    if (!container) {

        const errorElement = document.createElement('p');
        errorElement.className = 'text-danger';
        errorElement.innerText = errorMessage;
        container.innerHTML = '';
        container.appendChild(errorElement);
    }
};

/**
 * Generates HTML for a user avatar.
 * @param {string} user_id - The user ID.
 * @param {number} [size=30] - The size of the avatar (optional).
 * @returns {string} - The generated HTML string.
 */
export const generateUserAvatarHTML = (user_id, size = 30) => {
    const userDetails = userCache[user_id].profile;
    const avatarUrl = userDetails.avatarUrl || DEFAULT_AVATAR;
    return `
        <div class="avatar-container" id="avatar-container-${user_id}">
            <img src="${avatarUrl}" alt="avatar" width="${size}" height="${size}" class="rounded-circle object-fit-cover">
            <span class="status-indicator status-indicator-${user_id}" id="status-indicator-${user_id}"></span>
        </div>
    `;
};


/**
 * Fills the user cache with user details if they are not already present.
 *
 * @param {Array} users - An array of user objects.
 * @param {number} users[].user_id - The unique identifier for a user.
 * @returns {Promise<void>} A promise that resolves when the user cache is filled.
 *
 * @throws {Error} Will log an error message if fetching user details fails.
 */
export const fillUserCache = async (users) => {
  for (const user of users) {
    if (!userCache[user.user_id]) {
      try {
        const userDetails = await fetchUserDetails(user.user_id);
        userCache[user.user_id] = userDetails;
      } catch (error) {
          showToast('Error fetching user details for user_id:', user.user_id, error);
      }
    }
  }
  // Call initializeOnlineStatusSubscriptions after updating the cache
  initializeOnlineStatusSubscriptions();
};

/**
 * Updates the online status indicator for a given user.
 *
 * @param {number|string} userId - The ID of the user whose status is being updated.
 * @param {boolean} status - The online status of the user. `true` for online (green), `false` for offline (red).
 */
const updateOnlineStatus = (userId, status) => {
  const statusIndicators = document.querySelectorAll(`#status-indicator-${userId}`);
  statusIndicators.forEach(indicator => {
    indicator.style.backgroundColor = status ? 'green' : 'red';
  });
};

/**
 * Initializes online status subscriptions for users.
 * Iterates over the userCache and subscribes to the online status of users
 * who are not already subscribed.
 *
 * @throws Will log an error message to the console if an error occurs during initialization.
 */
export const initializeOnlineStatusSubscriptions = () => {
  try {
    Object.keys(userCache).forEach(userId => {
      if (!subscribedUsers.has(userId)) {
        subscribedUsers.add(userId);
        subscribeToOnlineStatus(parseInt(userId, 10), updateOnlineStatus);
      }
    });
  } catch (error) {
      showToast('Error initializing online status subscriptions:', error);
  }
};

export { userCache };
