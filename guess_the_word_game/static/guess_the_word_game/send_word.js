function showToast(text = 'Ошибка', title = 'Системное сообщение') {
    const toastLive = document.getElementById('liveToast');
    const toast = new bootstrap.Toast(toastLive);
    toastLive.querySelector('.toast-title').textContent = title;
    toastLive.querySelector('.toast-body').textContent = text;
    toast.show();
}

const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Обработчик отправки формы
document.getElementById("removeWordForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Предотвращение отправки формы по умолчанию
    $.ajax({
        url: window.location.href,
        type: 'GET',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'csrfmiddlewaretoken': csrftoken,
            'remove_word': $('#remove_word').val(),
        },
        success: function (response) {
            // Обработка успешного ответа
            console.log(response)
            if (response) {
                showToast(response);
            }
            $('#remove_word').val('');
        },
        error: function (error) {
            // Обработка ошибки
            console.log(error);
        }
    });

});


document.getElementById("randomWordForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Предотвращение отправки формы по умолчанию
    $.ajax({
        url: window.location.href,
        type: 'GET',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'csrfmiddlewaretoken': csrftoken,
            'dif': $('#inputDifGroupSelect').val()
        },
        success: function (response) {
            $('#random_noun').html(response.noun)
            $('#meaning').html(response.meaning);
        },
        error: function (error) {
            // Обработка ошибки
            console.log(error);
        }
    });
});
