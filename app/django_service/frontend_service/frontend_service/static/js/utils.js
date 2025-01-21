// utils.js
import { SubscriptionClient } from 'https://cdn.jsdelivr.net/npm/subscriptions-transport-ws@0.9.18/+esm';
import {ApolloClient, InMemoryCache, HttpLink, gql as gqlPars } from 'https://esm.sh/@apollo/client@3.3.19';
import { split } from "https://cdn.jsdelivr.net/npm/apollo-link@1.2.14/+esm";
import { getMainDefinition } from 'https://cdn.jsdelivr.net/npm/apollo-utilities@1.3.4/+esm';
import { WebSocketLink } from 'https://cdn.jsdelivr.net/npm/apollo-link-ws@1.0.20/+esm';

const protocol = window.location.protocol === "https:" ? "https:" : "http:";
const wsProtocol = protocol === "https:" ? "wss:" : "ws:";
const host = window.location.host;
const httpUrl = `${protocol}//${host}/graphql/`;
const wsUrl = `${wsProtocol}//${host}/graphql/`;

const httpLink = new HttpLink({
  uri: httpUrl,
});

const subscriptionClient = new SubscriptionClient(
  'wss://localhost/graphql',
  {
    reconnect: true,
    timeout: 20000,
    lazy: false,
  }
);

subscriptionClient.onConnected(() => console.log("[DEBUG] WebSocket connected."));
subscriptionClient.onReconnected(() => console.log("[DEBUG] WebSocket reconnected."));
subscriptionClient.onDisconnected(() => console.log("[DEBUG] WebSocket disconnected."));
subscriptionClient.onError((error) => console.error("[DEBUG] WebSocket error:", error));
subscriptionClient.onReconnecting(() => {
  console.log("[DEBUG] Attempting to reconnect to:", subscriptionClient.url);
});
subscriptionClient.client.onmessage = (message) => {
  console.log("[DEBUG] Message from server:", message.data);
};

const wsLink = new WebSocketLink( subscriptionClient);

const splitLink = split(
  ({ query }) => {
    console.log("[DEBUG] Incoming Query in SplitLink:", query);

    if (!query) {
      console.error("[DEBUG] Query is undefined or null!");
      return false;
    }
    const definition = getMainDefinition(query);

    console.log("[DEBUG] Main Definition Extracted:", definition);

    if (!definition) {
      console.error("[DEBUG] getMainDefinition returned null or undefined!");
      return false;
    }
    console.log("[DEBUG] SplitLink Routing:", {
      operation: definition.operation,
      operationName: definition.name ? definition.name.value : "Unnamed",
    });
    if (!definition.operation) {
      console.error("[DEBUG] Operation type is missing in definition!");
      return false;
    }
    return definition.operation === "subscription";
  },
  wsLink,
  httpLink
);

const Client = new ApolloClient({
    cache: new InMemoryCache(),
    link: splitLink,
});
/**
 * Executes a query using the HTTP client.
 * @param {Object} query - GraphQL query.
 * @param {Object} variables - GraphQL query variables.
 * @returns {Promise<Object>} - Query result.
 */
export async function executeQuery(query, variables = {}) {
    try {
        const result = await Client.query({
            query,
            variables,
        });
        return result.data;
    } catch (error) {
        console.error("[DEBUG] Query Error:", error);
        throw error;
    }
}

/**
 * Executes a mutation using the HTTP client.
 * @param {Object} mutation - GraphQL mutation.
 * @param {Object} [variables] - Variables for the mutation (optional).
 * @returns {Promise<Object>} - Mutation result.
 */
export async function executeMutation(mutation, variables = {}) {
    try {
        const result = await Client.mutate({
            mutation,
            variables,
        });
        return result.data;
    } catch (error) {
        console.error("[DEBUG] Mutation Error:", error);
        throw error;
    }
}
import { getOperationAST, parse } from "https://cdn.jsdelivr.net/npm/graphql@15.8.0/+esm";

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
  try {
    if (!Client) {
      const error = new Error("[DEBUG] Apollo Client is not initialized.");
      console.error(error.message);
      onError(error);
      return;
    }
    if (!subscriptionQuery || !subscriptionQuery.query) {
  console.error("[DEBUG] Invalid subscription query:", subscriptionQuery);
  throw new Error("Invalid subscription query. Ensure the 'query' field contains a valid GraphQL subscription.");
}
    console.log("[DEBUG] Executing subscription...");


    const observable = Client.subscribe({
      query: subscriptionQuery.query,
      variables: subscriptionQuery.variables || {},
    });

    return observable.subscribe({
      next: onNext,
      error: onError,
      complete: onComplete,
    });
  } catch (error) {
    console.error("[DEBUG] Failed to execute subscription:", error);
    onError?.(error);
  }
}


export const gql = gqlPars;

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