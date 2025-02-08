const NUM_ROWS = 6;
const NUM_COLS = 7;
const BORDER = 4;
const START_TARGET = 200;
const MARKER = "#marker";
const GAME_FIELD = "#game-field";
const GameStates = {PICK: 'pick', REVERT: 'revert', SWITCH: 'switch', REMOVE: 'remove', REFILL: 'refill', FALL: 'fall'};
const Flash = {HORIZONTAL: 'horizontal-flash', VERTICAL: 'vertical-flash', DOUBLE: 'double-flash', RAINBOW: 'rainbow'};
const GEM_CLASS = "gem";
const BEAM_CLASS = "beam";
const GEM_ID_PREFIX = "gem";
const bgColors = ["magenta", "mediumblue", "yellow", "lime", "cyan", "orange", "crimson", "gray"];
let difficulty = 4;
let modalActive = false;
let posX;
let posY;
let GEM_SIZE = 96;
let selectedRow = -1;
let selectedCol = -1;
let board = null;
let jewels = [];
let movingItems = 0;
let gameState = GameStates.PICK;
let swiped = false;
let swipeStart = null;
let multiplyScore = 1;
let idleTimeout = null;
const levelDifficulty = [3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 8, 8];
const modalOptions = {backdrop: 'static', keyboard: false};
let modalBackdrop;
let modal;
let modalBtn;
let modalBtnCancel;

document.addEventListener("DOMContentLoaded", function () {
    modalBackdrop = document.getElementById('staticBackdrop');
    modal = new bootstrap.Modal(modalBackdrop);
    modalBtn = modalBackdrop.querySelector('.btn');
    modalBtnCancel = modalBackdrop.querySelector('.btn-cancel');
});

function getImg(index) {
    const url = 'https://cache.foreca.net/static/img/symb-100x100/';
    const img_class = `<img class = "img-fluid pointer-events" src="`
    const img = [
        `d440.png" alt="Гроза">`,
        `n000.png" alt="Месяц">`,
        `d000.png" alt="Солнце">`,
        `d400.png" alt="Тучи">`,
        `d430.png" alt="Дождь">`,
        `d432.png" alt="Снег">`,
        `d220.png" alt="Пасмурно">`,
        `n220.png" alt="Пасмурно ночь">`,
    ];
    return img_class + url + img [index];
}


function refreshVariables() {
    multiplyScore = 1;
    selectedRow = -1;
    selectedCol = -1;
    movingItems = 0;
    gameState = GameStates.PICK;
    swiped = false;
    swipeStart = null;
    modalActive = false;
}
