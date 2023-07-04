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
        clearInterval(idleTimeout);
        gameOver("Поздравляем с победой! Ваш результат: " + accountValues.score, "Вы победили!", true);
        sendScore(accountValues.score, accountValues.level);
        accountValues.level++
        difficulty = (accountValues.level < 12) ? levelDifficulty[accountValues.level] : 8;
        accountValues.target = START_TARGET * accountValues.level;
    } else if (is_lose()) {
        clearInterval(idleTimeout);
        gameOver('К сожалению, ходы закончились. Возможно, повезёт в другой раз.  Уровень : ' + accountValues.level
            + ' Счёт: ' + accountValues.score, 'Игра окончена', false);
        accountValues.target = START_TARGET;
        accountValues.level = 1;
        difficulty = 4;
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
                  primary = false, second_btn = false) {
    modalActive = true;
    modalBackdrop.querySelector('#staticBackdropLabel').textContent = title;
    modalBackdrop.querySelector('.modal-body').textContent = text;
    // modalBackdrop.querySelector('#modal_result').textContent = accountValues.score;
    if (second_btn) {
        modalBtnCancel.classList.remove("visually-hidden");
    }
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

function closeModalAndCancel() {
    if (endFall()) {
        modal.hide();
        modalActive = false;
        modalBtnCancel.classList.add("visually-hidden")
    }
}

function closeModal() {
    if (endFall()) {
        modal.hide();
        if (!modalBtnCancel.classList.contains("visually-hidden")) {
            modalBtnCancel.classList.add("visually-hidden")
        } else restartGame();
        modalActive = false;
    }
}

function closeModalAndRestart() {
    if (endFall()) {
        modal.hide();
        if (!modalBtnCancel.classList.contains("visually-hidden")) {
            accountValues.target = START_TARGET;
            accountValues.level = 1;
            modalBtnCancel.classList.add("visually-hidden")
        }
        restartGame();
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
const modalBtnCancel = modalBackdrop.querySelector('.btn-cancel');

function sendScore(score, level) {
    if (level > 7) {
        const token = document.querySelector('[name=csrfmiddlewaretoken]').value;
        $.ajax({
            url: window.location.href,
            type: 'GET',
            headers: {'X-CSRFToken': token},
            data: {
                'csrfmiddlewaretoken': token,
                'score': score,
                'level': level,
            },
            success: function (response) {
                console.log(response)
            },
            error: function (error) {
                console.log(error);
            }
        });
    }
}

function start_new_game() {
    modalActive = true;
    gameOver('Прогресс будет сброшен и игра начнётся с первого уровня', 'Вы уверены?', false, true);
}