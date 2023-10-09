const inputElement = document.getElementById("my_input");

function createNewKeyboard() {
    const keyboard = document.getElementById('keyboard');
    let linesCode = createNewLineKeys('Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ');
    linesCode += createNewLineKeys('Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э');
    linesCode += createNewLineKeys('Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю');
    keyboard.innerHTML = linesCode;
    // Разукрашивает клавиатуру
    const letters = document.querySelector('#words').querySelectorAll('.letter');
    letters.forEach(function (letter) {
        const letterBtn = document.getElementById(letter.textContent);
        letterBtn.classList.add(...letter.classList);
    });
    // Добавление буквы с виртуальной клавиатуры в поле input
    keyboard.querySelectorAll('.border').forEach(function (key) {
        key.addEventListener("click", function () {
            if (inputElement.value.length < parseInt(difficulty)) inputElement.value += this.textContent;
        });
    });

    function createNewLineKeys(...keys) {
        let linesCode = `<div class="row justify-content-center my-2">`;
        keys.forEach(function (key) {
            linesCode += `<div class="btn btn-outline-secondary col-1 border" id="` + key + `">` + key + `</div>`;
        });
        return linesCode + `</div>`;
    }
}

createNewKeyboard();

function deleteSymbol() {
    inputElement.value = inputElement.value.slice(0, -1);
}

