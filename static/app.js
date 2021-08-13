[].slice
    .call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    .forEach(function (popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });

if (window.location.pathname === '/chat') {
    const chatGroups = [
        {
            id: 124,
            users: ['test2'],
            messages: [
                {
                    user: 'test2',
                    message: 'hey',
                    date: new Date(Date.now() - 1000 * 60 * 5)
                },
                {
                    user: 'test',
                    message: 'hi.',
                    date: new Date(Date.now() - 1000 * 60 * 4)
                }
            ]
        },
        {
            id: 123,
            users: ['test3', 'test4'],
            messages: [
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test3',
                    message: 'lorem ipsum dolar set amit',
                    date: new Date(Date.now() - 1000 * 60 * 10)
                },
                {
                    user: 'test4',
                    message: 'what???',
                    date: new Date(Date.now() - 1000 * 60 * 8)
                }
            ]
        }
    ];

    let activeGroupIdx = 0;

    const groupListDiv = document.getElementById('group-list');

    const refreshChatGroupList = () => {
        groupListDiv.innerHTML = '';

        for (const [i, group] of Object.entries(chatGroups)) {
            const a = document.createElement('a');
            a.className = 'list-group-item list-group-item-action';

            if (activeGroupIdx === Number(i)) {
                a.className += ' active';
            }

            a.innerText = group.users.join(', ');
            a.href = `#group-${group.id}`;

            a.onclick = () => {
                activeGroupIdx = Number(i);

                refreshChatGroupList();
                refreshChatRoom();
            };

            groupListDiv.appendChild(a);
        }
    };

    const chatRoomDiv = document.getElementById('chat-room');

    const addMessage = ({ user, message, date }) => {
        const span = document.createElement('span');

        span.innerHTML =
            `<strong>${user}</strong> <em>(${date.toLocaleString()})</em>:`;

        const p = document.createElement('p');
        p.innerText = message;

        chatRoomDiv.appendChild(span);
        chatRoomDiv.appendChild(p);
        //chatRoomDiv.appendChild(document.createElement('hr'));

        chatRoomDiv.scrollTop = chatRoomDiv.scrollHeight;
    };

    const usersUl = document.getElementById('user-list');

    const refreshChatRoom = () => {
        usersUl.innerHTML = '';

        const active = chatGroups[activeGroupIdx];

        for (const user of active.users) {
            const li = document.createElement('li');
            li.innerText = user;
            usersUl.appendChild(li);
        }

        chatRoomDiv.innerHTML = '';

        for (const message of active.messages) {
            addMessage(message);
        }
    };

    refreshChatGroupList();
    refreshChatRoom();
}
