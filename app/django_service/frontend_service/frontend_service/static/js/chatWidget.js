import { fetchChatRoomDetails, fetchChatRoomMessages, subscribeToUserChatRooms, subscribeToChatRoomMessages, sendChatRoomMessage, fetchUserDetails } from './chatservice.js';
import { showError } from './utils.js';
import { addMessageToContainer, createElement, DEFAULT_AVATAR, formatDate, formatTime } from './domHelpers.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatRoomList = document.getElementById('chatRoomList');
    const chatRoomMessagesContainer = document.getElementById('chat-Room-Messages');
    const toggleButton = document.getElementById('toggleOffcanvasButton');
    const offcanvas = document.getElementById('offcanvasBottom');
    const closeButton = document.getElementById('closeOffcanvasButton');
    const messageInput = document.getElementById('chatMessageInput');
    const sendMessageButton = document.getElementById('sendChatMessageButton');

    const NO_MESSAGES_TEXT = 'No messages in this chat room.';
    const userCache = {}; // Cache to store user details

    /**
     * Populates chat room messages in the UI.
     * @param {number} chatRoomId - ID of the chat room.
     */
    const populateChatRoomMessages = (chatRoomId) => {
        chatRoomMessagesContainer.innerHTML = '';

        const onMessageUpdate = async (message) => {
            const { timestamp, sender_id, content } = message.data.chat_room_message;
            const messageDate = formatDate(timestamp);
            const formattedTime = formatTime(timestamp);
            let lastMessageDate = null;

            // Check if the user is in the cache
            if (!userCache[sender_id]) {
                try {
                    // Fetch user details and update the cache
                    const userDetails = await fetchUserDetails(sender_id);
                    userCache[sender_id] = userDetails["profile"];
                    console.log('User details:', userDetails);
                } catch (error) {
                    console.error('Error fetching user details:', error);
                    showError(chatRoomMessagesContainer, 'Failed to load user details. Please try again.');
                    return;
                }
            }

            const user = userCache[sender_id];
            const avatar = user.avatarUrl || DEFAULT_AVATAR;
            const nickname = user.nickname || `User ${sender_id}`;

            if (lastMessageDate !== messageDate) {
                const dateElement = createElement('li', messageDate, 'text-center my-3', {
                    color: '#ffffff'
                });
                chatRoomMessagesContainer.appendChild(dateElement);
                lastMessageDate = messageDate;
            }

            const messageElement = createElement(
                'li',
                `
                    <img src="${avatar}" alt="avatar" class="rounded-circle d-flex align-self-start me-3 shadow-1-strong" width="60" style="flex-shrink: 0;">
                    <div class="card flex-grow-1">
                        <div class="card-header d-flex justify-content-between py-1 px-2">
                            <p class="text-muted mb-0" style="font-size: 0.875rem;">${nickname}</p>
                            <p class="text-muted small mb-0">
                                <i class="far fa-clock"></i> ${formattedTime}
                            </p>
                        </div>
                        <div class="card-body" style="background-color: #202020; color: #ffffff;">
                            <p class="mb-0">${content}</p>
                        </div>
                    </div>
                `,
                'chat-message d-flex align-items-start mb-3', {
                maxWidth: '100%'
            }
            );
            chatRoomMessagesContainer.appendChild(messageElement);
        };

        const onError = (error) => {
            console.error('Error populating messages:', error);
            showError(chatRoomMessagesContainer, 'Failed to load messages. Please try again.');
        };

        subscribeToChatRoomMessages(chatRoomId, onMessageUpdate, onError);
    };

    const sendMessage = async () => {
        const chatRoomId = document.querySelector('.chat-room.active').dataset.chatRoomId;
        const messageContent = messageInput.value.trim();

        if (messageContent) {
            try {
                await sendChatRoomMessage(chatRoomId, messageContent);
                messageInput.value = '';
            } catch (error) {
                console.error('Error sending message:', error);
                showError(chatRoomMessagesContainer, 'Failed to send message. Please try again.');
            }
        }
    }

    /**
     * Selects and fetches messages for a given chat room.
     * @param {Object} room - Selected chat room object.
     */
    const selectChatRoom = (room) => {
        document.querySelectorAll('.chat-room').forEach((el) => el.classList.remove('active'));
        document.querySelector(`[data-chat-room-id="${room.id}"]`).classList.add('active');
        populateChatRoomMessages(room.id);
    };

    const loadChatRoomData = async () => {
        try {
            // Clear out any existing chat rooms and display a loading message
            chatRoomList.innerHTML = '<li class="text-light">Loading chat rooms...</li>';

            // Maintain a set of chat room IDs already displayed in the UI
            const existingRoomIds = new Set();

            // Subscribe to real-time updates for chat rooms
            const subscribe = subscribeToUserChatRooms(
                (room) => {
                    console.log('Subscription data:', room);
                    room = room.data.chatRoomsForUser;
                    // If the chat room is not already in the DOM, add it
                    if (!existingRoomIds.has(room.id)) {
                        existingRoomIds.add(room.id); // Track added chat room

                        // Create and add the chat room element to the list
                        const newRoomElement = createElement(
                            'li',
                            `
                                <a href="#!" class="d-flex justify-content-between">
                                    <div class="d-flex flex-row">
                                        <img src="${DEFAULT_AVATAR}" alt="avatar" width="60" class="rounded-circle me-3">
                                        <div>
                                            <p class="fw-bold">${room.name}</p>
                                        </div>
                                    </div>
                                </a>
                            `,
                            'chat-room p-2 border-bottom',
                            { color: '#ffffff' },
                            { 'data-chat-room-id': room.id }
                        );

                        // Remove the "loading" or "waiting" placeholder, if present
                        const noChatRoomsPlaceholder = chatRoomList.querySelector('.text-light');
                        if (noChatRoomsPlaceholder) {
                            noChatRoomsPlaceholder.remove();
                        }

                        // Append the new chat room to the UI list
                        chatRoomList.appendChild(newRoomElement);

                        // Add an event listener for chat room selection
                        newRoomElement.querySelector('a').addEventListener('click', () => selectChatRoom(room));
                    }
                },
                (error) => {
                    console.error("Subscription error:", error);
                    showError(chatRoomList, "Failed to load chat rooms.");
                }
            );

            // Update the placeholder if no updates arrive immediately
            chatRoomList.innerHTML = '<li class="text-light">Waiting for chat rooms...</li>';

            // Optionally, provide a way to stop the subscription later
            // Save `unsubscribe` to use it when needed (e.g., when navigating away)
            //window.chatRoomUnsubscriber = unsubscribe;
        } catch (error) {
            console.error("Error loading chat rooms:", error);

            // Display an error message in the UI
            showError(chatRoomList, "Failed to load chat rooms.");
        }
    };

    const toggleOffcanvas = () => {
        const isVisible = offcanvas.classList.toggle('show');
        Object.assign(offcanvas.style, {
            visibility: isVisible ? 'visible' : 'hidden',
            height: isVisible ? '50vh' : '0'
        });
    };

    sendMessageButton?.addEventListener('click', sendMessage);
    toggleButton?.addEventListener('click', toggleOffcanvas);
    closeButton?.addEventListener('click', toggleOffcanvas);
    loadChatRoomData();
});
