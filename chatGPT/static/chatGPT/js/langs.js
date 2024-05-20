async function submitLangForm() {
    const formData = new FormData(document.getElementById('languageForm'));
    const url = "/i18n/setlang/";
    // const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    localStorage.setItem("language", formData.get('language'));
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            // headers: {
            //     'X-CSRFToken': csrftoken, // В Django для CSRF-токена обычно требуется этот заголовок
            // },
            // credentials: 'same-origin' // Для корректной работы с CSRF-токеном
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        window.location.reload();
    } catch (error) {
        console.error('Ошибка при отправке формы:', error);
    }
}