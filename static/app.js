[].slice
    .call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    .forEach(function (popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });

const socket = io();

if (window.location.pathname === '/chat') {
    // [ { id, users } ]
    let chatGroups = [];

    // [ { user, message, date } ]
    let chatMessages = [];

    socket.on('connect', () => {
        socket.emit('get-chat-groups', {});
    });

    socket.on('chat-groups', (groups) => {
        chatGroups = groups;
        console.log(chatGroups);
        refreshChatGroupList();
    });

    socket.on('chat-messages', (messages) => {
        chatMessages = messages;
        refreshChatRoom();
    });

    let activeGroupIdx = -1;

    const chatWithInput = document.getElementById('chat-with');

    chatWithInput.onkeyup = (e) => {
        if (e.key === 'Enter') {
            console.log('open new chat with username');
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
                activeGroupIdx = Number(i);

                socket.emit('get-chat-messages', {
                    group_id: chatGroups[activeGroupIdx].id
                });

                refreshChatGroupList();
                refreshChatRoom();
            };

            groupListDiv.appendChild(a);
        }
    };

    const chatRoomDiv = document.getElementById('chat-room');

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
        if (e.key === 'Enter') {
            console.log('send message');
        }
    };

    //refreshChatGroupList();
    //refreshChatRoom();
}
