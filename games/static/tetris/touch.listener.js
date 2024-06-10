//Чувствительность — количество пикселей, после которого жест будет считаться свайпом
const sensitivity = 20;

touchMoves = {
    ["Swipe Left"]: p => ({...p, x: p.x - 1}),
    ["Swipe Right"]: p => ({...p, x: p.x + 1}),
    ["Swipe Down"]: p => ({...p, y: p.y + 1}),
    // ["Double Touch"]: p => ({ ...p, y: p.y + 1 }),
    ["Touch"]: p => board.rotate(p)
};

let touchStart = null; //Точка начала касания
let touchPosition = null; //Текущая позиция
let touchLength = null; //Количество одновременных нажатий
let touchMoved = false;

//Перехватываем события
document.addEventListener("touchstart", function (e) {
    TouchStart(e);
}); //Начало касания
document.addEventListener("touchmove", function (e) {
    TouchMove(e);
}); //Движение пальцем по экрану
//Пользователь отпустил экран
document.addEventListener("touchend", function (e) {
    TouchEnd(e);
});
//Отмена касания
document.addEventListener("touchcancel", function (e) {
    TouchEnd(e);
});

function TouchStart(e) {
    //Получаем текущую позицию касания
    touchStart = {x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY};
    touchPosition = {x: touchStart.x, y: touchStart.y};
    touchLength = e.touches.length;
    touchMoved = false;
}

function TouchMove(e) {
    //Получаем новую позицию
    touchPosition = {x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY};
    let msg = CheckAction();
    if (msg !== '') {
        touchControl(msg);
        touchMoved = true;
        touchStart = {x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY};
    }

}

function TouchEnd(e) {
    touchPosition = {x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY};
    if (!touchMoved && !CheckMoveSensitivity()) {
        touchControl("Touch");
    }
    //Очищаем позиции
    touchLength = null;
    touchStart = null;
    touchPosition = null;
    touchMoved = false;
}

function CheckMoveSensitivity() {
    let d = //Получаем расстояния от начальной до конечной точки по обеим осям
        {
            x: touchStart.x - touchPosition.x,
            y: touchStart.y - touchPosition.y
        };
    return Math.max(Math.abs(d.x), Math.abs(d.y)) > sensitivity

}

function CheckAction() {
    let d = //Получаем расстояния от начальной до конечной точки по обеим осям
        {
            x: touchStart.x - touchPosition.x,
            y: touchStart.y - touchPosition.y
        };

    let msg = ""; //Сообщение

    if (CheckMoveSensitivity()) {
        if (Math.abs(d.x) > Math.abs(d.y)) //Проверяем, движение по какой оси было длиннее
        {
            if (d.x > 0) //Если значение больше нуля, значит пользователь двигал пальцем справа налево
            {
                msg = "Swipe Left";
            } else //Иначе он двигал им слева направо
            {
                msg = "Swipe Right";
            }
        } else //Аналогичные проверки для вертикальной оси
        {
            if (!touchMoved) {
                if (d.y > 0) //Свайп вверх
                {
                    msg = "Swipe Up";
                } else //Свайп вниз
                {
                    msg = "Swipe Down";
                }
                touchMoved = true;
            }
        }
    }
    return msg; //Выводим сообщение

}


function touchControl(msg) {
    if (msg === "Swipe Up") {
        pause();
    } else if (requestId && touchMoves[msg]) {
        // Get new state
        let p = touchMoves[msg](board.piece);
        if (msg === "Swipe Down") {
            // Hard drop
            while (board.valid(p)) {
                account.score += POINTS.HARD_DROP;
                board.piece.move(p);
                p = moves["ArrowDown"](board.piece);
            }
        } else if (board.valid(p)) {
            board.piece.move(p);
            if (msg === "Swipe Down") {
                account.score += POINTS.SOFT_DROP;
            }
        }
    }
}


const btnMaxi = document.querySelector('#maximize');
const btnMini = document.querySelector('#minimize');
/* Get the documentElement (<html>) to display the page in fullscreen */
const elem = document.documentElement;

/* View in fullscreen */
function maximize() {
    try {
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) { /* Safari */
            elem.webkitRequestFullscreen();
        } else showToast("iPhone не поддерживает открытие страницы на весь экран.");
        btnMaxi.classList.add('visually-hidden');
        btnMini.classList.remove('visually-hidden');
    } catch (e) {
        showToast("iPhone не поддерживает открытие страницы на весь экран.");
    }
}

/* Close fullscreen */
function minimize() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) { /* Safari */
        document.webkitExitFullscreen();
    }
    btnMini.classList.add('visually-hidden');
    btnMaxi.classList.remove('visually-hidden');
}