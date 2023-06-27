function showToast(text = 'Ошибка', title = 'Системное сообщение') {
    const toastLive = document.getElementById('liveToast');
    const toast = new bootstrap.Toast(toastLive);
    toastLive.querySelector('.toast-title').textContent = title;
    toastLive.querySelector('.toast-body').textContent = text;
    toast.show();
}

// Обработчик отправки формы
document.getElementById("removeWordForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Предотвращение отправки формы по умолчанию

    // Получение значения из input
    const inputText = document.getElementById("remove_word").value;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    $.ajax({
        url: window.location.href,
        type: 'GET',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'csrfmiddlewaretoken': csrftoken,
            'remove_word': inputText,
        },
        success: function (response) {
            // Обработка успешного ответа
            console.log(response)
            if (response) {
                showToast(response);
            }
        },
        error: function (error) {
            // Обработка ошибки
            console.log(error);
        }
    });
});

