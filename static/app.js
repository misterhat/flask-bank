[].slice
    .call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    .forEach(function (popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });

const socket = io();

socket.on('error-message', (error) => {
    alert(error);
});

if (window.location.pathname === '/chat') {
    // { groupID: unread }
    const unreadGroupds = {};

    // [ { id, users } ]
    let chatGroups = [];

    // [ { user, message, date } ]
    let chatMessages = [];

    socket.on('connect', () => {
        socket.emit('get-chat-groups', {});
    });

    socket.on('redirect', (loc) => {
        window.location = loc;
        window.location.hash = '';
        window.location.reload();
    });

    socket.on('chat-groups', (groups) => {
        chatGroups = groups;


        if (window.location.hash.slice(1,6) === 'group') {
            const joinGroupID = Number(window.location.hash.slice(7));

            for (const [i, group] of Object.entries(chatGroups)) {
                if (group.id === joinGroupID) {
                    goToRoomIdx(i);
                    return;
                }
            }
        } else {
            refreshChatGroupList();
        }
    });

    socket.on('chat-messages', (messages) => {
        chatMessages = messages;
        refreshChatRoom();
    });

    socket.on('chat-message', (message) => {
        console.log('got message', message);
        const activeGroup = chatGroups[activeGroupIdx];

        if (activeGroup && activeGroup.id == message.group_id) {
            addMessage(message);
        }
    });

    let activeGroupIdx = -1;

    const goToRoomIdx = (idx) => {
        activeGroupIdx = Number(idx);

        socket.emit('get-chat-messages', {
            group_id: chatGroups[activeGroupIdx].id
        });

        refreshChatGroupList();
        refreshChatRoom();
    };

    const chatWithInput = document.getElementById('chat-with');

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

    const groupListDiv = document.getElementById('group-list');

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

    const chatRoomDiv = document.getElementById('chat-room');

    const addMessage = ({ user, message, date }) => {
        user = user || 'System';
        date = new Date(date * 1000);

        const span = document.createElement('span');

        span.innerHTML = `<strong>${user}</strong> <em>(${date.toLocaleString()})</em>:`;

        const p = document.createElement('p');
        p.innerText = message;

        chatRoomDiv.appendChild(span);
        chatRoomDiv.appendChild(p);

        chatRoomDiv.scrollTop = chatRoomDiv.scrollHeight;
    };

    const chatRoomWrapDiv = document.getElementById('chat-room-wrap');
    const chatRoomMessageDiv = document.getElementById('chat-room-message');
    const usersUl = document.getElementById('user-list');

    const refreshChatRoom = () => {
        if (!chatGroups.length || activeGroupIdx === -1) {
            chatRoomWrapDiv.style.display = 'none';
            chatRoomMessageDiv.style.display = 'block';
            return;
        }

        chatRoomMessageDiv.style.display = 'none';
        chatRoomWrapDiv.style.display = 'block';

        usersUl.innerHTML = '';

        const active = chatGroups[activeGroupIdx];

        for (const user of active.users) {
            const li = document.createElement('li');
            li.innerText = '👤 ' + user;
            usersUl.appendChild(li);
        }

        chatRoomDiv.innerHTML = '';

        for (const message of chatMessages) {
            addMessage(message);
        }
    };

    const messageInput = document.getElementById('message');

    messageInput.onkeyup = (e) => {
        const message = messageInput.value.trim();

        if (e.key === 'Enter' && message.length) {
            socket.emit('send-message', {
                group_id: chatGroups[activeGroupIdx].id,
                message
            });

            messageInput.value = '';
        }
    };

    const leaveGroupButton = document.getElementById('leave-group');

    leaveGroupButton.onclick = (e) => {
        socket.emit('leave-group', {
            group_id: chatGroups[activeGroupIdx].id
        });
    };
} else {
    // notification
    socket.on('chat-message', (message) => {
        console.log('got message', message);
    });
}
