document.addEventListener('DOMContentLoaded', () => {
    const chatRoomList = document.getElementById('chatRoomList');
    const toggleButton = document.getElementById('toggleOffcanvasButton');
    const offcanvas = document.getElementById('offcanvasBottom');
    const closeButton = document.getElementById('closeOffcanvasButton');
    const graphqlEndpoint = '/graphql/';
    const chatRoomMessagesContainer = document.getElementById('chat-Room-Messages');
//@ToDo: needs to be gernalist and refactored

    const fetchGraphQL = async (query) => {
        try {
            const response = await fetch(graphqlEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
                credentials: 'include'
            });

            if (response.ok) {
                const result = await response.json();
                if (result.errors) throw new Error('GraphQL Errors');
                return result.data;
            } else {
                throw new Error(`Network error: ${response.statusText}`);
            }
        } catch (error) {
            console.error('GraphQL request failed:', error);
            throw error;
        }
    };

    const fetchChatRoomMessages = async (chatRoomId) => {
        const query = `
            query GetChatRoomMessages {
                chatRoom(id: ${chatRoomId}) {
                    messages {
                        chatRoomId
                        content
                        senderId
                        id
                        timestamp
                    }
                }
            }
        `;

        try {
            const data = await fetchGraphQL(query);
            return data.chatRoom.messages;
        } catch (error) {
            console.error('Failed to fetch chat room messages:', error);
            throw error;
        }
    };

    const populateChatRoomMessages = async (chatRoomId) => {
        chatRoomMessagesContainer.innerHTML = '';

        try {
            const messages = await fetchChatRoomMessages(chatRoomId);
            let lastMessageDate = null;

            messages.forEach((message) => {
                const messageDate = new Date(message.timestamp).toDateString();
                const messageTime = new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                });

                if (lastMessageDate !== messageDate) {
                    const dateSeparator = document.createElement('li');
                    dateSeparator.className = 'text-center my-3';
                    dateSeparator.style.color = '#ffffff';
                    dateSeparator.innerText = messageDate;
                    chatRoomMessagesContainer.appendChild(dateSeparator);
                    lastMessageDate = messageDate;
                }

                const messageElement = document.createElement('li');
                messageElement.className = 'chat-message d-flex align-items-start mb-3';
                messageElement.style.maxWidth = '100%';
                messageElement.innerHTML = `
                    <img src="https://via.placeholder.com/50"
                         alt="avatar"
                         class="rounded-circle d-flex align-self-start me-3 shadow-1-strong"
                         width="60"
                         style="flex-shrink: 0;">
                    <div class="card flex-grow-1">
                        <div class="card-header d-flex justify-content-between py-1 px-2">
                            <p class="text-muted mb-0" style="font-size: 0.875rem;">User ${message.senderId}</p>
                            <p class="text-muted small mb-0">
                                <i class="far fa-clock"></i> ${messageTime}
                            </p>
                        </div>
                        <div class="card-body" style="background-color: #202020; color: #ffffff;">
                            <p class="mb-0">${message.content}</p>
                        </div>
                    </div>
                `;
                chatRoomMessagesContainer.appendChild(messageElement);
            });

            if (messages.length === 0) {
                const noMessagesElement = document.createElement('li');
                noMessagesElement.className = 'p-2 ';
                noMessagesElement.innerText = 'No messages in this chat room.';
                noMessagesElement.style.color = '#ffffff';
                noMessagesElement.style.backgroundColor = '#181818';
                chatRoomMessagesContainer.appendChild(noMessagesElement);
            }
        } catch (error) {
            console.error('Failed to populate chat room messages:', error);
            const errorElement = document.createElement('li');
            errorElement.className = 'p-2 text-danger';
            errorElement.innerText = 'Failed to load messages. Please try again.';
            chatRoomMessagesContainer.appendChild(errorElement);
        }
    };

    const buildChatRoomDetailsQuery = (ids) => `
        query {
            ${ids.map((id, i) => `chatRoom${i + 1}: chatRoom(id: ${id}) { id name users { userId } }`).join('\n')}
        }`;

    const loadChatRoomData = async () => {
        try {
            const idsResponse = await fetchGraphQL(`query { chatRoomsForUser { id } }`);
            const ids = idsResponse.chatRoomsForUser.map((room) => room.id);

            if (ids.length === 0) {
                chatRoomList.innerHTML = '<li>No chat rooms available</li>';
                return;
            }

            const detailsQuery = buildChatRoomDetailsQuery(ids);
            const detailsResponse = await fetchGraphQL(detailsQuery);

            const rooms = ids.map((id, index) => detailsResponse[`chatRoom${index + 1}`]);
            renderChatRooms(rooms);
        } catch {
            chatRoomList.innerHTML = '<li style="color:red">Failed to load chat rooms</li>';
        }
    };

    const renderChatRooms = (rooms) => {
        chatRoomList.innerHTML = rooms.map((room) => `
            <li class="chat-room p-2 border-bottom" data-chat-room-id="${room.id}" style="color: #ffffff;">
                <a href="#!" class="d-flex justify-content-between">
                    <div class="d-flex flex-row">
                        <img src="https://via.placeholder.com/50" alt="avatar" width="60" class="rounded-circle me-3">
                        <div>
                            <p class="fw-bold">${room.name}</p>
                        </div>
                    </div>
                </a>
            </li>
        `).join('');

        document.querySelectorAll('.chat-room a').forEach((link, i) => {
            link.addEventListener('click', () => selectChatRoom(rooms[i]));
        });
    };

    const selectChatRoom = (room) => {
        console.log('Selected room:', room);
        document.querySelectorAll('.chat-room').forEach((el) => el.classList.remove('active'));
        document.querySelector(`[data-chat-room-id="${room.id}"]`).classList.add('active');
        populateChatRoomMessages(room.id);
    };

    const toggleOffcanvas = () => {
        const isVisible = offcanvas.classList.toggle('show');
        offcanvas.style.visibility = isVisible ? 'visible' : 'hidden';
        offcanvas.style.height = isVisible ? '50vh' : '0';
    };

    toggleButton?.addEventListener('click', toggleOffcanvas);
    closeButton?.addEventListener('click', toggleOffcanvas);
    loadChatRoomData();
});