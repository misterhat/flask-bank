const socket = io();

socket.on('error-message', (error) => {
    alert(error);
});

if (window.location.pathname === '/chat') {
    // state variables:

    // { groupID: unread }
    const unreadGroupds = {};

    // [ { id, users } ]
    let chatGroups = [];

    let activeGroupIdx = -1;

    // [ { user, message, date } ]
    let chatMessages = [];

    const getActiveGroup = () => {
        return chatGroups[activeGroupIdx];
    };

    // socket events:

    socket.on('connect', () => {
        socket.emit('get-chat-groups', {});
    });

    socket.on('redirect', (loc) => {
        window.location.hash = '';
        window.location = loc;
        window.location.reload();
    });

    socket.on('refresh-chat-groups', (userID) => {
        if (userID) {
            if (userID === window.BANK_USER_ID) {
                socket.emit('get-chat-groups', {});
            }
        } else {
            socket.emit('get-chat-groups', {});
        }
    });

    socket.on('chat-groups', (groups) => {
        let active = getActiveGroup();
        const activeID = active ? active.id : -1;

        chatGroups = groups;

        if (activeID > -1) {
            let newIdx = -1;

            for (const [i, { id }] of Object.entries(chatGroups)) {
                if (id === activeID) {
                    newIdx = Number(i);
                    break;
                }
            }

            activeGroupIdx = newIdx;
            active = getActiveGroup();
        } else if (window.location.hash.slice(1,6) === 'group') {
            const joinGroupID = Number(window.location.hash.slice(7));

            for (const [i, group] of Object.entries(chatGroups)) {
                if (group.id === joinGroupID) {
                    goToRoomIdx(i);
                    break;
                }
            }
        }

        refreshChatRoom();

        if (active) {
            refreshChatUsers();
        }

        refreshChatGroupList();
    });

    socket.on('chat-messages', (messages) => {
        chatMessages = messages;
        refreshChatRoom();
    });

    socket.on('chat-message', (message) => {
        const activeGroup = getActiveGroup();

        if (activeGroup && activeGroup.id == message.group_id) {
            chatMessages.push(message);
            addMessage(message);
        }
    });

    // element definitions:

    const chatWithInput = document.getElementById('chat-with');
    const groupListDiv = document.getElementById('group-list');
    const chatRoomDiv = document.getElementById('chat-room');
    const chatRoomWrapDiv = document.getElementById('chat-room-wrap');
    const chatRoomMessageDiv = document.getElementById('chat-room-message');
    const usersUl = document.getElementById('user-list');
    const messageInput = document.getElementById('message');
    const inviteInput = document.getElementById('invite');
    const leaveGroupButton = document.getElementById('leave-group');

    // element re-draw functions:

    const refreshChatGroupList = () => {
        groupListDiv.innerHTML = '';

        for (const [i, group] of Object.entries(chatGroups)) {
            const a = document.createElement('a');
            a.className = 'list-group-item list-group-item-action';

            if (activeGroupIdx === Number(i)) {
                a.className += ' active';
            }

            // 👤 👥
            a.innerText = group.users.join(', ');
            a.href = `#group-${group.id}`;

            a.onclick = () => {
                goToRoomIdx(i);
            };

            groupListDiv.appendChild(a);
        }
    };

    const addMessage = ({ user, message, date }) => {
        user = user || 'System';
        date = new Date(date * 1000);

        const span = document.createElement('span');

        span.innerHTML =
            `<strong>${user}</strong> <em>(${date.toLocaleString()})</em>:`;

        const p = document.createElement('p');
        p.innerText = message;

        chatRoomDiv.appendChild(span);
        chatRoomDiv.appendChild(p);

        // scroll to the bottom
        chatRoomDiv.scrollTop = chatRoomDiv.scrollHeight;
    };

    const refreshChatUsers = () => {
        usersUl.innerHTML = '';

        const active = getActiveGroup();

        if (!active) {
            return;
        }

        for (const user of active.users) {
            const li = document.createElement('li');
            li.innerText = '👤 ' + user;
            usersUl.appendChild(li);
        }
    };

    const refreshChatRoom = () => {
        if (!chatGroups.length || activeGroupIdx === -1) {
            chatRoomWrapDiv.style.display = 'none';
            chatRoomMessageDiv.style.display = 'block';
            return;
        }

        chatRoomMessageDiv.style.display = 'none';
        chatRoomWrapDiv.style.display = 'block';

        refreshChatUsers();

        chatRoomDiv.innerHTML = '';

        for (const message of chatMessages) {
            addMessage(message);
        }
    };

    // helpers:

    const goToRoomIdx = (idx) => {
        activeGroupIdx = Number(idx);

        socket.emit('get-chat-messages', {
            group_id: getActiveGroup().id
        });

        refreshChatGroupList();
        refreshChatRoom();
    };

    // element event handlers:

    chatWithInput.onkeyup = (e) => {
        const username = chatWithInput.value.trim();

        if (e.key === 'Enter' && username.length) {
            chatWithInput.value = '';

            for (const [i, { users }] of Object.entries(chatGroups)) {
                if (users.length === 1 && users[0] === username) {
                    goToRoomIdx(i);
                    return;
                }
            }

            socket.emit('create-group', { username });
        }
    };

    messageInput.onkeyup = (e) => {
        const message = messageInput.value.trim();

        if (e.key === 'Enter' && message.length) {
            socket.emit('send-message', {
                group_id: getActiveGroup().id,
                message
            });

            messageInput.value = '';
        }
    };

    inviteInput.onkeyup = (e) => {
        const username = inviteInput.value.trim().toLowerCase();

        if (e.key === 'Enter' && username.length) {
            inviteInput.value = '';

            for (const user of chatGroups[activeGroupIdx].users) {
                if (user.toLowerCase() === username) {
                    alert(`${username} is already in the group.`);
                    return;
                }
            }

            socket.emit('invite-group', {
                group_id: chatGroups[activeGroupIdx].id,
                username
            });
        }

    };

    leaveGroupButton.onclick = (e) => {
        if (confirm("Are you sure you wish to leave the group?")) {
            socket.emit('leave-group', {
                group_id: getActiveGroup().id
            });
        }
    };
} else {
    const notification = document.getElementById('message-notification');
    const notificationToast = new bootstrap.Toast(notification);

    // notification
    socket.on('chat-message', ({ group_id, user, message }) => {
        notification.querySelector('.me-auto').innerText =
          `Message from ${user}`;

        notification.querySelector('.toast-message').innerText = message;

        notification.querySelector('.link-primary').href =
          `/chat#group-${group_id}`;

        notificationToast.show();
    });
}
