export const graphqlEndpoint = '/graphql/';

/**
 * Generic function to send GraphQL requests.
 * @param {string} query - The GraphQL query string.
 * @returns {Promise<any>} The data response from the server.
 */
export const fetchGraphQL = async (query) => {
    try {
        const response = await fetch(graphqlEndpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query}),
            credentials: 'include',
        });

        if (response.ok) {
            const result = await response.json();
            if (result.errors) throw new Error(result.errors[0]?.message ?? 'GraphQL Errors');
            return result.data;
        } else {
            throw new Error(`Network error: ${response.statusText}`);
        }
    } catch (err) {
        console.error('GraphQL request failed:', err);
        throw err;
    }
};

/**
 * Adds an error message to a container for display.
 * @param {HTMLElement} container - The DOM container to append the error message.
 * @param {string} errorMessage - The error message to display.
 */
export const showError = (container, errorMessage) => {
    const errorElement = document.createElement('p');
    errorElement.className = 'text-danger';
    errorElement.innerText = errorMessage;
    container.innerHTML = ''; // Clear any previous errors
    container.appendChild(errorElement);
};