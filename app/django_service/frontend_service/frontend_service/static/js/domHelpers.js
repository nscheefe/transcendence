// utils/domHelpers.js

export const DEFAULT_AVATAR = 'https://via.placeholder.com/50';
export const DEFAULT_USER_AVATAR = 'https://via.placeholder.com/100';

/**
 * Creates an HTML element with optional attributes and styles.
 * @param {string} tagName - The type of the element (e.g., 'li', 'div').
 * @param {string | null} innerHTML - The HTML to set as the element's content.
 * @param {string} [className] - The class name(s) to assign to the element.
 * @param {Object} [styles={}] - Inline styles to apply to the element.
 * @param {Object} [attributes={}] - Additional attributes to set (e.g., id, data-*).
 * @returns {HTMLElement} The newly created element.
 */
export const createElement = (tagName, innerHTML = null, className = '', styles = {}, attributes = {}) => {
    const element = document.createElement(tagName);

    if (innerHTML) element.innerHTML = innerHTML;
    if (className) element.className = className;
    Object.assign(element.style, styles);
    Object.entries(attributes).forEach(([key, value]) => {
        element.setAttribute(key, value);
    });

    return element;
};

/**
 * Formats a timestamp into a human-readable time string (HH:mm).
 * @param {string} timestamp - The timestamp to format.
 * @returns {string} The formatted time string.
 */
export const formatTime = (timestamp) =>
    new Date(timestamp).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});

/**
 * Formats a timestamp into a human-readable date string.
 * @param {string} timestamp - The timestamp to format.
 * @returns {string} The formatted date string.
 */
export const formatDate = (timestamp) => new Date(timestamp).toDateString();

/**
 * Clears the contents of a container and adds a single message.
 * @param {HTMLElement} container - The container to modify.
 * @param {string} message - The message to display.
 * @param {string} [className=''] - Optional class names for styling.
 */
export const addMessageToContainer = (container, message, className = '') => {
    container.innerHTML = '';
    const messageElement = createElement('p', message, className);
    container.appendChild(messageElement);
};