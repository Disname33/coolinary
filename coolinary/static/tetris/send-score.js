function showToast(text = 'Ошибка', title = 'Системное сообщение') {
    const toastLive = document.getElementById('liveToast');
    const toast = new bootstrap.Toast(toastLive);
    toastLive.querySelector('.toast-title').textContent = title;
    toastLive.querySelector('.toast-body').textContent = text;
    toast.show();
}

function sendScore() {
    if (account.score > 1000) {
        const csrftoken2 = document.querySelector('[name=csrfmiddlewaretoken]').value;
        $.ajax({
            url: window.location.href,
            type: 'GET',
            headers: {'X-CSRFToken': csrftoken2},
            data: {
                'csrfmiddlewaretoken': csrftoken2,
                'score': account.score,
                'lines': account.lines,
                'level': account.level,
            },
            success: function (response) {
                // Обработка успешного ответа
                console.log(response)
                showToast("Ваш результат добавлен в таблицу рекордов")
                // setTimeout(toastBootstrap.hide(), 5000);
            },
            error: function (error) {
                // Обработка ошибки
                console.log(error);
            }
        });
    }
}