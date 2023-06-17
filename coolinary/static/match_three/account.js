let accountValues = {
    level: 1,
    score: 0,
    moves: 20,
    target: START_TARGET
}

function updateAccount(key, value) {
    let element = document.getElementById(key);
    if (element) {
        element.textContent = value;
    }
}

function is_win() {
    return accountValues.score >= accountValues.target
}

function is_lose() {
    return accountValues.moves < 1;
}

function checkAccount() {
    if (is_win()) {
        gameOver("Поздравляем с победой! Ваш результат: " + accountValues.score, "Вы победили!", true);
        accountValues.level++
        difficultly = (accountValues.level < 12) ? levelDifficultly[accountValues.level] : 8;
        accountValues.target = START_TARGET * accountValues.level;
    } else if (is_lose()) {
        gameOver('К сожалению ходы закончились. Может в другой раз повезёт.', 'Игра окончена', false);
        accountValues.target = START_TARGET;
        accountValues.level = 1;
    } else modalActive = false;
}

let account = new Proxy(accountValues, {
    set: (target, key, value) => {
        target[key] = value;
        updateAccount(key, value);
        if (!modalActive) {
            modalActive = true;
            waitForCondition(checkAccount);
        }
        return true;
    }
});


function gameOver(text = 'Ошибка.',
                  title = 'Системное сообщение.',
                  primary = false) {
    modalActive = true;
    modalBackdrop.querySelector('#staticBackdropLabel').textContent = title;
    modalBackdrop.querySelector('.modal-body').textContent = text;
    if (primary) {
        modalBtn.classList.remove("btn-secondary");
        modalBtn.classList.add("btn-primary");
        modalBtn.innerHTML = "Следующий уровень"
    } else {
        modalBtn.classList.remove("btn-primary");
        modalBtn.classList.add("btn-secondary");
        modalBtn.innerHTML = "Начать с начала"
    }
    waitForCondition(function () {
        modal.show(options)
    });
}



function closeModal() {
    if (endFall()) {
        restartGame();
        modal.hide();
        modalActive = false;
    }
}

function waitForCondition(callback) {
    const intervalId = setInterval(function () {
        if (endFall()) {
            clearInterval(intervalId);
            return callback();
        }
    }, 100); // Период проверки условия (в миллисекундах)
}

function endFall() {
    return $(".remove").length === 0 && $(".switch").length === 0 && $(".fall").length === 0
}

const modalBackdrop = document.getElementById('staticBackdrop');
const options = {
    backdrop: 'static', // Запретить закрытие модального окна при нажатии на фон
    keyboard: false // Запретить закрытие модального окна при нажатии на клавишу Esc
};
const modal = new bootstrap.Modal(modalBackdrop);
const modalBtn = modalBackdrop.querySelector('.btn');