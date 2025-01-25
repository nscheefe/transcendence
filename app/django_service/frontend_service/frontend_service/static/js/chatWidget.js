import { fetchChatRoomDetails, fetchChatRoomMessages, subscribeToUserChatRooms, subscribeToChatRoomMessages, sendChatRoomMessage, fetchUserDetails } from './chatservice.js';
import { blockUser, fetchFriendships } from './friendservice.js';
import { showError } from './utils.js';
import { addMessageToContainer, createElement, DEFAULT_AVATAR, formatDate, formatTime } from './domHelpers.js';

const userCache = {}; // Cache to store user details

const fillUserCache = async (users) => {
    for (const user of users) {
        if (!userCache[user.user_id]) {
            try {
                const userDetails = await fetchUserDetails(user.user_id);
                userCache[user.user_id] = userDetails.profile;
            } catch (error) {
                console.error('Error fetching user details:', error);
            }
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const chatRoomList = document.getElementById('chatRoomList');
    const chatRoomMessagesContainer = document.getElementById('chat-Room-Messages');
    const toggleButton = document.getElementById('toggleOffcanvasButton');
    const offcanvas = document.getElementById('offcanvasBottom');
    const closeButton = document.getElementById('closeOffcanvasButton');
    const messageInput = document.getElementById('chatMessageInput');
    const sendMessageButton = document.getElementById('sendChatMessageButton');

    const NO_MESSAGES_TEXT = 'No messages in this chat room.';
    let lastMessageDate = null; // Track the date of the last message

    /**
     * Populates chat room messages in the UI.
     * @param {number} chatRoomId - ID of the chat room.
     */
    const populateChatRoomMessages = async (chatRoomId) => {
        chatRoomMessagesContainer.innerHTML = '';
        let friendships = await fetchFriendships(); // Await the result of fetchFriendships
        console.log('Fetched Friendships:', friendships);

        friendships = Array.isArray(friendships) ? friendships.flat() : Object.values(friendships).flat(); // Ensure friendships is an array
        console.log('Processed Friendships:', friendships);

        let blockedUsers = friendships.filter(friendship => friendship.blocked).map(friendship => friendship.friendId);
        console.log('Blocked users:', blockedUsers);

        const onMessageUpdate = async (message) => {
            const { timestamp, sender_id, content } = message.data.chat_room_message;
            if (blockedUsers.includes(sender_id)) {
                return;
            }
            const messageDate = formatDate(timestamp);
            const formattedTime = formatTime(timestamp);

            // Check if the user is in the cache
            if (!userCache[sender_id]) {
                try {
                    // Fetch user details and update the cache
                    await fillUserCache([{ user_id: sender_id }]);
                    console.log('User details:', userCache[sender_id]);
                } catch (error) {
                    console.error('Error fetching user details:', error);
                    showError(chatRoomMessagesContainer, 'Failed to load user details. Please try again.');
                    return;
                }
            }

            const user = userCache[sender_id];
            const avatar = user.avatarUrl || DEFAULT_AVATAR;
            const nickname = user.nickname || `User ${sender_id}`;
            const own_nickname = document.querySelector('.intra-name-42').innerText;
            const isOwnMessage = nickname == own_nickname;
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
                <div class="d-flex ${isOwnMessage ? 'flex-row-reverse align-self-end' : 'flex-row align-self-start'}">
                <div class="d-flex flex-column align-items-center">
                    <img src="${avatar}" alt="avatar" class="rounded-circle d-flex ${isOwnMessage ? 'ms-3' : 'me-3'} shadow-1-strong" width="60" style="flex-shrink: 0;">
                    <p class="text-light small mb-0">
                        <i class="far fa-clock ms-1"></i> ${formattedTime}
                    </p>
                </div>
                    <div class="card flex-grow-1 ${isOwnMessage ? 'text-end' : 'text-start'}">
                        <div class="card-header d-flex ${isOwnMessage ? 'justify-content-end' : 'justify-content-start'} py-1">
                            <p class="text-muted mb-0" style="font-size: 0.875rem;">${nickname}</p>
                        </div>
                        <div class="card-body" style="background-color: #202020; color: #ffffff;">
                            <p class="mb-0">${content}</p>
                        </div>
                    </div>
                </div>
                `,
                'chat-message d-flex flex-row ${isOwnMessage ? justify-content-end : justify-content-start} mb-3', {
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
                async (room) => {
                    console.log('Subscription data:', room);
                    room = room.data.chatRoomsForUser;

                    // Fill user cache
                    await fillUserCache(room.users);

                    // If the chat room is not already in the DOM, add it
                    if (!existingRoomIds.has(room.id)) {
                        existingRoomIds.add(room.id); // Track added chat room

                        if (room.name.includes('User-to-User')) {
                            const userIds = room.name.match(/\d+/g);
                            if (userIds && userIds.length === 2) {
                                const user1 = userCache[userIds[0]];
                                const user2 = userCache[userIds[1]];
                                room.name = `Chat of ${user1.nickname} and ${user2.nickname}`;
                            }
                        }
                        // Generate the list of avatars
                        const avatars = room.users.map(user => {
                            const userDetails = userCache[user.user_id];
                            return `<img src="${userDetails.avatarUrl || DEFAULT_AVATAR}" alt="avatar" width="30" height="30" class="rounded-circle object-fit-cover">`;
                        }).join('');

                        // Create and add the chat room element to the list
                        const newRoomElement = createElement(
                            'li',
                            `
                                <a href="#!" class="d-flex justify-content-between">
                                <div class="d-flex flex-column">
                                    <div>
                                        <p class="fw-bold">${room.name}</p>
                                    </div>
                                    <div class="d-flex flex-row pt-1">
                                        ${avatars}
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
