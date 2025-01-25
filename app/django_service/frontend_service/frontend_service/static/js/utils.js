import { SubscriptionClient } from 'https://cdn.jsdelivr.net/npm/@httptoolkit/subscriptions-transport-ws@0.11.2/+esm';
// utils.js
import { parse } from "https://cdn.jsdelivr.net/npm/graphql@15.8.0/+esm";
const protocol = window.location.protocol === "https:" ? "https:" : "http:";
const wsProtocol = protocol === "https:" ? "wss:" : "ws:";
const host = window.location.host;
const httpUrl = `${protocol}//${host}/graphql/`;
const wsUrl = `${wsProtocol}//${host}/graphql/`;

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
    console.error("[DEBUG] GraphQL errors:", result.errors);
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

    console.log("[DEBUG] Mutation Request Body:", body); // Log the request body

    try {
        const response = await fetch(httpUrl, {
            method: 'POST',
            headers: headers,
            body: body,
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("[DEBUG] HTTP Error Response:", errorText); // Log the error response
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.errors) {
            console.error("[DEBUG] GraphQL errors:", result.errors);
        }
        return result.data;
    } catch (error) {
        console.error("[DEBUG] Mutation Error:", error);
        throw error;
    }
}

/**
 * Executes a subscription using the WebSocket client.
 * @param {Object|string} subscriptionQuery - A raw query string with variables or parsed query object.
 * @param {Function} [onNext] - Callback to handle subscription updates.
 * @param {Function} [onError] - Callback to handle subscription errors.
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
    const errorElement = document.createElement('p');
    errorElement.className = 'text-danger';
    errorElement.innerText = errorMessage;
    container.innerHTML = '';
    container.appendChild(errorElement);
};
