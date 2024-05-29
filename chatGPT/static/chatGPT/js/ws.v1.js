let socket = new WebSocket(webSocket());

function webSocket() {
    const protocol = window.location.protocol === "http:" ? 'ws://' : 'wss://';
    return protocol + window.location.host + '/ws/chatGPT/'
}



function reloadSocket() {
    socket.close(1000, 'restart');
    socket = new WebSocket(webSocket());
    startNewSocket();
}

function startNewSocket(func = null) {
    // Обработчик успешного соединения
    socket.onopen = function (event) {
        console.log('WebSocket connected');
        if (func !== null) func();
    };

    // Обработчик входящих сообщений от сервера
    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.type && messageHandlers[data.type] && data.data) {
            messageHandlers[data.type](data.data);
        } else {
            console.warn('Unknown message type:', data.type);
        }
    };

    // Обработчик закрытия соединения
    socket.onclose = function (event) {
        console.log('WebSocket disconnected');
        // messageHandlers.error('Соединение с сервером разорвано! Обновите страницу!')
    };

    // Обработчик ошибок
    socket.onerror = function (error) {
        console.error('WebSocket error:', error);
        content_inner.innerHTML += `<p><strong>An error occured:</strong> ${error}</p>`;
    };
}

startNewSocket();

function new_connection_if_closed(func) {
    if (socket.readyState !== socket.OPEN) {
        socket = new WebSocket(webSocket());
        startNewSocket(func);
    } else func();
}

function close_connection() {
    socket.close(1000, 'close');
}

function send_data(data) {
    new_connection_if_closed(function () {
        socket.send(data);
    });
}

// Объект с функциями обработки различных типов сообщений
const messageHandlers = {
    conversation: function (data) {
        console.info("Conversation used:", data)
    },
    provider: function (data) {
        content.querySelector('.provider').innerHTML = `
                        <a href="${data.url}" target="_blank">
                            ${data.label ? data.label : data.name}
                        </a>
                        ${data.model ? ' with ' + data.model : ''}
                    `
    },
    message: function (data) {
        console.error('Error:', data);
        content_inner.innerHTML += `<p><strong>Ошибка:</strong> ${data}</p>`;
        close_connection();
    },
    preview: function (data) {
        content_inner.innerHTML = markdown_render(data);
    },
    content: function (data) {
        // console.log('Content:', data);
        text += data;
        html = markdown_render(text);
        let lastElement, lastIndex = null;
        for (element of ['</p>', '</code></pre>', '</p>\n</li>\n</ol>', '</li>\n</ol>', '</li>\n</ul>']) {
            const index = html.lastIndexOf(element)
            if (index - element.length > lastIndex) {
                lastElement = element;
                lastIndex = index;
            }
        }
        if (lastIndex) {
            html = html.substring(0, lastIndex) + '<span id="cursor"></span>' + lastElement;
        }
        content_inner.innerHTML = html;
        content_count.innerText = count_words_and_tokens(text, provider_result?.model);
        highlight(content_inner);


        window.scrollTo(0, 0);
        if (message_box.scrollTop >= message_box.scrollHeight - message_box.clientHeight - 100) {
            message_box.scrollTo({top: message_box.scrollHeight, behavior: "auto"});
        }
    },
    error: function (data) {
        console.error('Server error:', data);
        content_inner.innerHTML += `<p><strong>Ошибка:</strong> ${data}</p>`;
        close_connection();
    },
    finish: function () {
        add_message(window.conversation_id, "assistant", text, provider_result);
        // load_conversation(window.conversation_id);
        html = markdown_render(text);
        content_inner.innerHTML = html;
        highlight(content_inner);

        imageInput.value = "";
        cameraInput.value = "";
        fileInput.value = "";
        for (const key in fileInput.dataset) {
            delete fileInput.dataset[key];
        }
        close_connection();
        console.log('Message finished');
    }
};

