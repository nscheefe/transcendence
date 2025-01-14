import {fetchChatRoomDetails, fetchChatRoomMessages, fetchUserChatRooms} from './chatservice.js';
import {showError} from './utils.js';
import {addMessageToContainer, createElement, DEFAULT_AVATAR, formatDate, formatTime} from './domHelpers.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatRoomList = document.getElementById('chatRoomList');
    const chatRoomMessagesContainer = document.getElementById('chat-Room-Messages');
    const toggleButton = document.getElementById('toggleOffcanvasButton');
    const offcanvas = document.getElementById('offcanvasBottom');
    const closeButton = document.getElementById('closeOffcanvasButton');

    const NO_MESSAGES_TEXT = 'No messages in this chat room.';

    /**
     * Populates chat room messages in the UI.
     * @param {number} chatRoomId - ID of the chat room.
     */
    const populateChatRoomMessages = async (chatRoomId) => {
        chatRoomMessagesContainer.innerHTML = '';
        try {
            const result = await fetchChatRoomMessages(chatRoomId);
            const messages = result?.chatRoom?.messages;
            let lastMessageDate = null;
            messages.forEach(({
                                  timestamp,
                                  senderId,
                                  content
                              }) => {
                const messageDate = formatDate(timestamp);
                const formattedTime = formatTime(timestamp);
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
                        <img src="${DEFAULT_AVATAR}" alt="avatar" class="rounded-circle d-flex align-self-start me-3 shadow-1-strong" width="60" style="flex-shrink: 0;">
                        <div class="card flex-grow-1">
                            <div class="card-header d-flex justify-content-between py-1 px-2">
                                <p class="text-muted mb-0" style="font-size: 0.875rem;">User ${senderId}</p>
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
            });
            if (messages.length === 0) {
                addMessageToContainer(chatRoomMessagesContainer, NO_MESSAGES_TEXT, 'p-2 text-light', {
                    backgroundColor: '#181818'
                });
            }
        } catch (error) {
            console.error('Error populating messages:', error);
            showError(chatRoomMessagesContainer, 'Failed to load messages. Please try again.');
        }
    };

    /**
     * Renders the chat room list in the sidebar.
     * @param {Array} rooms - Array of chat room details.
     */
    const renderChatRooms = (rooms) => {
        chatRoomList.innerHTML = rooms
            .map((room) =>
                createElement(
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
                    'chat-room p-2 border-bottom', {
                        color: '#ffffff'
                    }, {
                        'data-chat-room-id': room.id
                    }
                ).outerHTML
            )
            .join('');
        document.querySelectorAll('.chat-room a').forEach((link, i) => {
            link.addEventListener('click', () => selectChatRoom(rooms[i]));
        });
    };

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
        const userChatRoomsResponse = await fetchUserChatRooms();
        const userChatRooms = userChatRoomsResponse.chatRoomsForUser;
        if (!Array.isArray(userChatRooms) || userChatRooms.length === 0) {
            chatRoomList.innerHTML = '<li class="text-light">No chat rooms available.</li>';
            return;
        }
        const roomIds = [];
        for (let i = 0; i < userChatRooms.length; i++) {
            if (userChatRooms[i] && userChatRooms[i].id) {
                roomIds.push(userChatRooms[i].id);
            } else {
                console.error(`Invalid chat room entry at index ${i}:`, userChatRooms[i]);
            }
        }
        console.log("Room IDs:", roomIds);
        if (roomIds.length === 0) {
            chatRoomList.innerHTML = '<li class="text-light">No valid chat rooms found.</li>';
            return;
        }
        const roomDetails = await fetchChatRoomDetails(roomIds);
        renderChatRooms(roomDetails);
    } catch (error) {
        console.error("Error loading chat rooms:", error);
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

    toggleButton?.addEventListener('click', toggleOffcanvas);
    closeButton?.addEventListener('click', toggleOffcanvas);
    loadChatRoomData();
});