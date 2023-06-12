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
                const toastLiveExample = document.getElementById('liveToast');
                const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample);
                toastBootstrap.show();
                // setTimeout(toastBootstrap.hide(), 5000);
            },
            error: function (error) {
                // Обработка ошибки
                console.log(error);
            }
        });
    }
}