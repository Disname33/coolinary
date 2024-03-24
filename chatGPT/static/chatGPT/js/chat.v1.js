const colorThemes = document.querySelectorAll('[name="theme"]');
const markdown = window.markdownit();
const message_box = document.getElementById(`messages`);
const messageInput = document.getElementById(`message-input`);
const box_conversations = document.querySelector(`.top`);
const stop_generating = document.querySelector(`.stop_generating`);
const regenerate = document.querySelector(`.regenerate`);
const sidebar = document.querySelector(".conversations");
const sidebar_button = document.querySelector(".mobile-sidebar");
const sendButton = document.getElementById("send-button");
const imageInput = document.getElementById("image");
const cameraInput = document.getElementById("camera");
const fileInput = document.getElementById("file");
const inputCount = document.getElementById("input-count")
const modelSelect = document.getElementById("model");
const systemPrompt = document.getElementById("systemPrompt")
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

let prompt_lock = false;

// hljs.addPlugin(new CopyButtonPlugin());

messageInput.addEventListener("blur", () => {
    window.scrollTo(0, 0);
});

messageInput.addEventListener("focus", () => {
    document.documentElement.scrollTop = document.documentElement.scrollHeight;
});

const markdown_render = (content) => {
    return markdown.render(content
        .replaceAll(/<!--.+-->/gm, "")
        .replaceAll(/<img data-prompt="[^>]+">/gm, "")
    )
        .replaceAll("<a href=", '<a target="_blank" href=')
        .replaceAll('<code>', '<code class="language-plaintext">')
}

let typesetPromise = Promise.resolve();
const highlight = (container) => {
    container.querySelectorAll('code:not(.hljs)').forEach((el) => {
        if (el.className !== "hljs") {
            hljs.highlightElement(el);
        }
    });
    typesetPromise = typesetPromise.then(
        () => MathJax.typesetPromise([container])
    ).catch(
        (err) => console.log('Typeset failed: ' + err.message)
    );
}

const register_remove_message = async () => {
    document.querySelectorAll(".message .fa-xmark").forEach(async (el) => {
        if (!("click" in el.dataset)) {
            el.dataset.click = "true";
            el.addEventListener("click", async () => {
                if (prompt_lock) {
                    return;
                }
                const message_el = el.parentElement.parentElement;
                await remove_message(window.conversation_id, message_el.dataset.index);
                await load_conversation(window.conversation_id, false);
            })
        }
    });
}

const delete_conversations = async () => {
    for (let i = 0; i < localStorage.length; i++) {
        let key = localStorage.key(i);
        if (key.startsWith("conversation:")) {
            localStorage.removeItem(key);
        }
    }
    await hide_sidebar();
    await new_conversation();
};

const handle_ask = async () => {
    messageInput.style.height = "82px";
    messageInput.focus();
    window.scrollTo(0, 0);

    message = messageInput.value
    if (message.length > 0) {
        messageInput.value = "";
        prompt_lock = true;
        await count_input()
        await add_conversation(window.conversation_id, message);
        if ("text" in fileInput.dataset) {
            message += '\n```' + fileInput.dataset.type + '\n';
            message += fileInput.dataset.text;
            message += '\n```'
        }
        let message_index = await add_message(window.conversation_id, "user", message);
        window.token = message_id();

        if (imageInput.dataset.src) URL.revokeObjectURL(imageInput.dataset.src);
        const input = imageInput && imageInput.files.length > 0 ? imageInput : cameraInput
        if (input.files.length > 0) imageInput.dataset.src = URL.createObjectURL(input.files[0]);
        else delete imageInput.dataset.src

        model = modelSelect.options[modelSelect.selectedIndex].value
        message_box.innerHTML += `
            <div class="message" data-index="${message_index}">
                <div class="user">
                    ${user_image}
                    <i class="fa-solid fa-xmark"></i>
                    <i class="fa-regular fa-phone-arrow-up-right"></i>
                </div>
                <div class="content" id="user_${token}"> 
                    <div class="content_inner">
                    ${markdown_render(message)}
                    ${imageInput.dataset.src
            ? '<img src="' + imageInput.dataset.src + '" alt="Image upload">'
            : ''
        }
                    </div>
                    <div class="count">${count_words_and_tokens(message, model)}</div>
                </div>
            </div>
        `;
        await register_remove_message();
        highlight(message_box);
        await ask_gpt();
    }
};

const remove_cancel_button = async () => {
    stop_generating.classList.add(`stop_generating-hiding`);

    setTimeout(() => {
        stop_generating.classList.remove(`stop_generating-hiding`);
        stop_generating.classList.add(`stop_generating-hidden`);
    }, 300);
};

const prepare_messages = (messages, filter_last_message = true) => {
    // Removes none user messages at end
    if (filter_last_message) {
        let last_message;
        while (last_message = messages.pop()) {
            if (last_message["role"] === "user") {
                messages.push(last_message);
                break;
            }
        }
    }

    // Remove history, if it's selected
    if (document.getElementById('history')?.checked) {
        if (filter_last_message) {
            messages = [messages.pop()];
        } else {
            messages = [messages.pop(), messages.pop()];
        }
    }

    let new_messages = [];
    if (messages) {
        for (i in messages) {
            new_message = messages[i];
            // Remove generated images from history
            new_message.content = new_message.content.replaceAll(
                /<!-- generated images start -->[\s\S]+<!-- generated images end -->/gm,
                ""
            )
            delete new_message["provider"];
            // Remove regenerated messages
            if (!new_message.regenerate) {
                new_messages.push(new_message)
            }
        }
    }

    // Add system message
    system_content = systemPrompt?.value;
    if (system_content) {
        new_messages.unshift({
            "role": "system",
            "content": system_content
        });
    }

    return new_messages;
}

const ask_gpt = async () => {
    regenerate.classList.add(`regenerate-hidden`);
    messages = await get_messages(window.conversation_id);
    total_messages = messages.length;

    messages = prepare_messages(messages);

    window.scrollTo(0, 0);
    window.controller = new AbortController();

    jailbreak = document.getElementById("jailbreak");
    provider = document.getElementById("provider");
    window.text = '';

    stop_generating.classList.remove(`stop_generating-hidden`);

    message_box.scrollTop = message_box.scrollHeight;
    window.scrollTo(0, 0);

    el = message_box.querySelector('.count_total');
    el ? el.parentElement.removeChild(el) : null;

    message_box.innerHTML += `
        <div class="message" data-index="${total_messages}">
            <div class="assistant">
                ${gpt_image}
                <i class="fa-solid fa-xmark"></i>
                <i class="fa-regular fa-phone-arrow-down-left"></i>
            </div>
            <div class="content" id="gpt_${window.token}">
                <div class="provider"></div>
                <div class="content_inner"><span id="cursor"></span></div>
                <div class="count"></div>
            </div>
        </div>
    `;
    content = document.getElementById(`gpt_${window.token}`);
    content_inner = content.querySelector('.content_inner');
    content_count = content.querySelector('.count');

    message_box.scrollTop = message_box.scrollHeight;
    window.scrollTo(0, 0);

    error = provider_result = null;
    try {
        let body = JSON.stringify({
            id: window.token,
            conversation_id: window.conversation_id,
            model: modelSelect.options[modelSelect.selectedIndex].value,
            jailbreak: jailbreak.options[jailbreak.selectedIndex].value,
            web_search: document.getElementById(`switch`).checked,
            provider: provider.options[provider.selectedIndex].value,
            patch_provider: document.getElementById('patch').checked,
            messages: messages
        });
        const headers = {
            'X-CSRFToken': csrftoken,
            // 'accept': 'text/event-stream',
            'content-type': 'application/json'
        }
        const input = imageInput && imageInput.files.length > 0 ? imageInput : cameraInput
        if (input && input.files.length > 0) {
            let formData = {};
            const reader = new FileReader();
            reader.onload = function (event) {
                const imageData = event.target.result;
                // Проверяем тип данных
                if (imageData instanceof ArrayBuffer) {
                    // Если тип данных ArrayBuffer, преобразуем его в Blob
                    const blob = new Blob([new Uint8Array(imageData)], {type: 'image/png'});
                    formData['image'] = blob.slice(5);
                } else {
                    formData['image'] = imageData.slice(5);
                }

                formData['json'] = body;
                send_data(JSON.stringify(formData));
            };
            reader.readAsDataURL(input.files[0]);


        } else {
            headers['content-type'] = 'application/json';
            //ws
            send_data(body);
        }
    } catch (e) {
        console.error(e);
        if (e.name !== "AbortError") {
            error = true;
            text = "oops ! something went wrong, please try again / reload. [stacktrace in console]";
            content_inner.innerHTML = text;
        } else {
            content_inner.innerHTML += " [aborted]";
            if (text) text += " [aborted]";
        }
    }
    if (!error && text) {
        await add_message(window.conversation_id, "assistant", text, provider_result);
        await load_conversation(window.conversation_id);
    } else {
        let cursorDiv = document.getElementById(`cursor`);
        if (cursorDiv) cursorDiv.parentNode.removeChild(cursorDiv);
    }
    window.scrollTo(0, 0);
    message_box.scrollTop = message_box.scrollHeight;
    await remove_cancel_button();
    await register_remove_message();
    prompt_lock = false;
    await load_conversations();
    regenerate.classList.remove("regenerate-hidden");
};

const clear_conversations = async () => {
    const elements = box_conversations.childNodes;
    let index = elements.length;

    if (index > 0) {
        while (index--) {
            const element = elements[index];
            if (
                element.nodeType === Node.ELEMENT_NODE &&
                element.tagName.toLowerCase() !== `button`
            ) {
                box_conversations.removeChild(element);
            }
        }
    }
};

const clear_conversation = async () => {
    let messages = message_box.getElementsByTagName(`div`);

    while (messages.length > 0) {
        message_box.removeChild(messages[0]);
    }
};

const show_option = async (conversation_id) => {
    const conv = document.getElementById(`conv-${conversation_id}`);
    const choi = document.getElementById(`cho-${conversation_id}`);

    conv.style.display = "none";
    choi.style.display = "block";
};

const hide_option = async (conversation_id) => {
    const conv = document.getElementById(`conv-${conversation_id}`);
    const choi = document.getElementById(`cho-${conversation_id}`);

    conv.style.display = "block";
    choi.style.display = "none";
};

const delete_conversation = async (conversation_id) => {
    localStorage.removeItem(`conversation:${conversation_id}`);

    const conversation = document.getElementById(`convo-${conversation_id}`);
    conversation.remove();

    if (window.conversation_id === conversation_id) {
        await new_conversation();
    }

    await load_conversations();
};

const set_conversation = async (conversation_id) => {
    history.pushState({}, null, `/chatGPT/chat/${conversation_id}`);
    window.conversation_id = conversation_id;

    await clear_conversation();
    await load_conversation(conversation_id);
    await load_conversations();
    await hide_sidebar();
};

const new_conversation = async () => {
    history.pushState({}, null, `/chatGPT/chat/`);
    window.conversation_id = uuid();

    await clear_conversation();
    if (systemPrompt) {
        systemPrompt.value = "";
    }
    await load_conversations();
    await hide_sidebar();
    await say_hello();
};

const load_conversation = async (conversation_id, scroll = true) => {
    let conversation = await get_conversation(conversation_id);
    let messages = conversation?.items || [];

    if (systemPrompt) {
        systemPrompt.value = conversation.system || "";
    }

    let elements = "";
    let last_model = null;
    for (i in messages) {
        let item = messages[i];
        last_model = item.provider?.model;
        let next_i = parseInt(i) + 1;
        let next_provider = item.provider ? item.provider : (messages.length > next_i ? messages[next_i].provider : null);

        let provider_link = item.provider?.name ? `<a href="${item.provider.url}" target="_blank">${item.provider.name}</a>` : "";
        let provider = provider_link ? `
            <div class="provider">
                ${provider_link}
                ${item.provider.model ? ' with ' + item.provider.model : ''}
            </div>
        ` : "";
        elements += `
            <div class="message${item.regenerate ? " regenerate" : ""}" data-index="${i}">
                <div class="${item.role}">
                    ${item.role === "assistant" ? gpt_image : user_image}
                    <i class="fa-solid fa-xmark"></i>
                    ${item.role === "assistant"
            ? `<i class="fa-regular fa-phone-arrow-down-left"></i>`
            : `<i class="fa-regular fa-phone-arrow-up-right"></i>`
        }
                </div>
                <div class="content">
                    ${provider}
                    <div class="content_inner">${markdown_render(item.content)}</div>
                    <div class="count">${count_words_and_tokens(item.content, next_provider?.model)}</div>
                </div>
            </div>
        `;
    }

    const filtered = prepare_messages(messages, false);
    if (filtered.length > 0) {
        last_model = last_model?.startsWith("gpt-4") ? "gpt-4" : "gpt-3.5-turbo"
        let count_total = GPTTokenizer_cl100k_base?.encodeChat(filtered, last_model).length
        if (count_total > 0) {
            elements += `<div class="count_total">(${count_total} tokens used)</div>`;
        }
    }

    message_box.innerHTML = elements;

    register_remove_message();
    highlight(message_box);

    if (scroll) {
        message_box.scrollTo({top: message_box.scrollHeight, behavior: "smooth"});

        setTimeout(() => {
            message_box.scrollTop = message_box.scrollHeight;
        }, 500);
    }
};

async function get_conversation(conversation_id) {
    return await JSON.parse(
        localStorage.getItem(`conversation:${conversation_id}`)
    );
}

async function save_conversation(conversation_id, conversation) {
    localStorage.setItem(
        `conversation:${conversation_id}`,
        JSON.stringify(conversation)
    );
}

async function get_messages(conversation_id) {
    let conversation = await get_conversation(conversation_id);
    return conversation?.items || [];
}

async function add_conversation(conversation_id, content) {
    if (content.length > 17) {
        title = content.substring(0, 17) + '...'
    } else {
        title = content + '&nbsp;'.repeat(19 - content.length)
    }

    if (localStorage.getItem(`conversation:${conversation_id}`) == null) {
        await save_conversation(conversation_id, {
            id: conversation_id,
            title: title,
            system: systemPrompt?.value,
            items: [],
        });
    }

    history.pushState({}, null, `/chatGPT/chat/${conversation_id}`);
}

async function save_system_message() {
    if (!window.conversation_id) return;
    const conversation = await get_conversation(window.conversation_id);
    conversation.system = systemPrompt?.value;
    await save_conversation(window.conversation_id, conversation);
}

const hide_last_message = async (conversation_id) => {
    const conversation = await get_conversation(conversation_id)
    const last_message = conversation.items.pop();
    if (last_message !== null) {
        if (last_message["role"] === "assistant") {
            last_message["regenerate"] = true;
        }
        conversation.items.push(last_message);
    }
    await save_conversation(conversation_id, conversation);
};

const remove_message = async (conversation_id, index) => {
    const conversation = await get_conversation(conversation_id);
    let new_items = [];
    for (i in conversation.items) {
        if (i === index - 1) {
            if (!conversation.items[index]?.regenerate) {
                delete conversation.items[i]["regenerate"];
            }
        }
        if (i !== index) {
            new_items.push(conversation.items[i])
        }
    }
    conversation.items = new_items;
    await save_conversation(conversation_id, conversation);
};

const add_message = async (conversation_id, role, content, provider) => {
    const conversation = await get_conversation(conversation_id);

    conversation.items.push({
        role: role,
        content: content,
        provider: provider
    });
    await save_conversation(conversation_id, conversation);
    return conversation.items.length - 1;
};

const load_conversations = async () => {
    let conversations = [];
    for (let i = 0; i < localStorage.length; i++) {
        if (localStorage.key(i).startsWith("conversation:")) {
            let conversation = localStorage.getItem(localStorage.key(i));
            conversations.push(JSON.parse(conversation));
        }
    }

    await clear_conversations();

    for (conversation of conversations) {
        box_conversations.innerHTML += `
            <div class="convo" id="convo-${conversation.id}">
                <div class="left" onclick="set_conversation('${conversation.id}')">
                    <i class="fa-regular fa-comments"></i>
                    <span class="convo-title">${conversation.title}</span>
                </div>
                <i onclick="show_option('${conversation.id}')" class="fa-regular fa-trash" id="conv-${conversation.id}"></i>
                <div id="cho-${conversation.id}" class="choise" style="display:none;">
                    <i onclick="delete_conversation('${conversation.id}')" class="fa-regular fa-check"></i>
                    <i onclick="hide_option('${conversation.id}')" class="fa-regular fa-x"></i>
                </div>
            </div>
        `;
    }
};

document.getElementById(`cancelButton`).addEventListener(`click`, async () => {
    // window.controller.abort();
    reloadSocket();
    console.log(`aborted ${window.conversation_id}`);
});

document.getElementById(`regenerateButton`).addEventListener(`click`, async () => {
    prompt_lock = true;
    reloadSocket();
    await hide_last_message(window.conversation_id);
    window.token = message_id();
    await ask_gpt();
});

const uuid = () => {
    return `xxxxxxxx-xxxx-4xxx-yxxx-${Date.now().toString(16)}`.replace(
        /[xy]/g,
        function (c) {
            let r = (Math.random() * 16) | 0,
                v = c === "x" ? r : (r & 0x3) | 0x8;
            return v.toString(16);
        }
    );
};

const message_id = () => {
    random_bytes = (Math.floor(Math.random() * 1338377565) + 2956589730).toString(
        2
    );
    unix = Math.floor(Date.now() / 1000).toString(2);

    return BigInt(`0b${unix}${random_bytes}`).toString();
};

async function hide_sidebar() {
    sidebar.classList.remove("shown");
    sidebar_button.classList.remove("rotated");
}

sidebar_button.addEventListener("click", (event) => {
    if (sidebar.classList.contains("shown")) {
        hide_sidebar();
    } else {
        sidebar.classList.add("shown");
        sidebar_button.classList.add("rotated");
    }

    window.scrollTo(0, 0);
});

const register_settings_localstorage = async () => {
    for (let id of ["switch", "model", "jailbreak", "patch", "provider", "history"]) {
        let element = document.getElementById(id);
        element.addEventListener('change', ((id) => {
            return (event) => {
                switch (event.target.type) {
                    case "checkbox":
                        localStorage.setItem(id, event.target.checked);
                        break;
                    case "select-one":
                        localStorage.setItem(id, event.target.selectedIndex);
                        break;
                    default:
                        console.warn("Unresolved element type");
                }
            };
        })(id));
    }
}

const load_settings_localstorage = async () => {
    for (id of ["switch", "model", "jailbreak", "patch", "provider", "history"]) {
        element = document.getElementById(id);
        value = localStorage.getItem(element.id);
        if (value) {
            switch (element.type) {
                case "checkbox":
                    element.checked = value === "true";
                    break;
                case "select-one":
                    element.selectedIndex = parseInt(value);
                    break;
                default:
                    console.warn("Unresolved element type");
            }
        }
    }
}

const say_hello = async () => {
    const tokens = {
        'ru': [`При`, `вет`, `!`, ` Чем`, ` я`, ` мо`, `гу`, ` по`, `мочь`, ` Вам`, ` се`, `го`, `дня`, `?`],
        'en': [`Hello`, `!`, ` How`, ` can`, ` I`, ` assist`, ` you`, ` today`, `?`],
        'fr': [`Bonjour`, `!`, ` Comment`, ` puis-je`, ` vous`, ` aider`, ` aujour`, `d'hui`, `?`],
        'es': [`¡Hola`, `!`, ` ¿Cómo`, ` puedo`, ` ayud`, `arte`, ` hoy`, `?`]
    };

    message_box.innerHTML += `
        <div class="message">
            <div class="assistant">
                ${gpt_image}
                <i class="fa-regular fa-phone-arrow-down-left"></i>
            </div>
            <div class="content">
                <p class=" welcome-message"></p>
            </div>
        </div>
    `;

    to_modify = document.querySelector(`.welcome-message`);
    for (token of tokens[localStorage.getItem('language')]) {
        await new Promise(resolve => setTimeout(resolve, (Math.random() * (100 - 200) + 100)))
        to_modify.textContent += token;
    }
}

// Theme storage for recurring viewers
const storeTheme = function (theme) {
    localStorage.setItem("theme", theme);
};

// set theme when visitor returns
const setTheme = function () {
    const activeTheme = localStorage.getItem("theme");
    colorThemes.forEach((themeOption) => {
        if (themeOption.id === activeTheme) {
            themeOption.checked = true;
        }
    });
    // fallback for no :has() support
    document.documentElement.className = activeTheme;
};

colorThemes.forEach((themeOption) => {
    themeOption.addEventListener("click", () => {
        storeTheme(themeOption.id);
        // fallback for no :has() support
        document.documentElement.className = themeOption.id;
    });
});

function count_tokens(model, text) {
    if (model) {
        if (model.startsWith("llama2") || model.startsWith("codellama")) {
            return llamaTokenizer?.encode(text).length;
        }
        if (model.startsWith("mistral") || model.startsWith("mixtral")) {
            return mistralTokenizer?.encode(text).length;
        }
    }
    return GPTTokenizer_cl100k_base?.encode(text).length;
}

function count_words(text) {
    return text.trim().match(/[\w\u4E00-\u9FA5]+/gu)?.length || 0;
}

function count_words_and_tokens(text, model) {
    return `(${count_words(text)} words, ${count_tokens(model, text)} tokens)`;
}

let countFocus = messageInput;
const count_input = async () => {
    if (countFocus.value) {
        model = modelSelect.options[modelSelect.selectedIndex].value;
        inputCount.innerText = count_words_and_tokens(countFocus.value, model);
    } else {
        inputCount.innerHTML = "&nbsp;"
    }
};
messageInput.addEventListener("keyup", count_input);
systemPrompt.addEventListener("keyup", count_input);
systemPrompt.addEventListener("focus", function () {
    countFocus = systemPrompt;
    count_input();
});
systemPrompt.addEventListener("blur", function () {
    countFocus = messageInput;
    count_input();
});

window.onload = async () => {
    setTheme();

    count_input();

    if (/\/chat\/.+/.test(window.location.href)) {
        load_conversation(window.conversation_id);
    } else {
        say_hello()
    }

    load_conversations();

    messageInput.addEventListener("keydown", async (evt) => {
        if (prompt_lock) return;

        if (evt.keyCode === 13 && !evt.shiftKey) {
            evt.preventDefault();
            console.log("pressed enter");
            await handle_ask();
        } else {
            messageInput.style.removeProperty("height");
            messageInput.style.height = messageInput.scrollHeight + "px";
        }
    });

    sendButton.addEventListener(`click`, async () => {
        console.log("clicked send");
        if (prompt_lock) return;
        await handle_ask();
    });

    messageInput.focus();

    register_settings_localstorage();
};

(async () => {
    response = await fetch('/chatGPT/backend-api/v2/models')
    models = await response.json()

    for (model of models) {
        let option = document.createElement('option');
        option.value = option.text = model;
        modelSelect.appendChild(option);
    }

    response = await fetch('/chatGPT/backend-api/v2/providers')
    providers = await response.json()
    select = document.getElementById('provider');

    for (provider of providers) {
        let option = document.createElement('option');
        option.value = option.text = provider;
        select.appendChild(option);
    }

    await load_settings_localstorage()
})();

for (const el of [imageInput, cameraInput]) {
    el.addEventListener('click', async () => {
        el.value = '';
        if (imageInput.dataset.src) {
            URL.revokeObjectURL(imageInput.dataset.src);
            delete imageInput.dataset.src
        }
    });
}

fileInput.addEventListener('click', async (event) => {
    fileInput.value = '';
    delete fileInput.dataset.text;
});
fileInput.addEventListener('change', async (event) => {
    if (fileInput.files.length) {
        type = fileInput.files[0].type;
        if (type && type.indexOf('/')) {
            type = type.split('/').pop().replace('x-', '')
            type = type.replace('plain', 'plaintext')
                .replace('shellscript', 'sh')
                .replace('svg+xml', 'svg')
                .replace('vnd.trolltech.linguist', 'ts')
        } else {
            type = fileInput.files[0].name.split('.').pop()
        }
        fileInput.dataset.type = type
        const reader = new FileReader();
        reader.addEventListener('load', (event) => {
            fileInput.dataset.text = event.target.result;
        });
        reader.readAsText(fileInput.files[0]);
    } else {
        delete fileInput.dataset.text;
    }
});

systemPrompt?.addEventListener("blur", async () => {
    await save_system_message();
});

async function submitForm() {
    const formData = new FormData(document.getElementById('languageForm'));
    const url = "/i18n/setlang/";
    localStorage.setItem("language", formData.get('language'));
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}', // В Django для CSRF-токена обычно требуется этот заголовок
            },
            credentials: 'same-origin' // Для корректной работы с CSRF-токеном
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        window.location.reload();
    } catch (error) {
        console.error('Ошибка при отправке формы:', error);
    }
}