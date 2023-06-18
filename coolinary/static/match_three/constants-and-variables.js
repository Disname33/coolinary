const NUM_ROWS = 6;
const NUM_COLS = 7;
const START_TARGET = 200;
const GEM_CLASS = "gem"
const GEM_ID_PREFIX = "gem";
const bgColors = ["magenta", "mediumblue", "yellow", "lime", "cyan", "orange", "crimson", "gray"];
let difficultly = 4;
let modalActive = false;
let posX;
let posY;
let GEM_SIZE = 96;
let selectedRow = -1;
let selectedCol = -1;
let jewels = [];
let movingItems = 0;
let gameState = "pick";
let swiped = false;
let swipeStart = null;
let multiplyScore = 1;
const levelDifficultly = [3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 8, 8];


function getImg(index) {
    const url = 'https://cache.foreca.net/static/img/symb-100x100/';
    const img_class = `<img class = "img-fluid pointer-events" src="`
    const img = [
        img_class + url + `d440.png" alt="Гроза">`,
        img_class + url + `n000.png" alt="Месяц">`,
        img_class + url + `d000.png" alt="Солнце">`,
        img_class + url + `d400.png" alt="Тучи">`,
        img_class + url + `d430.png" alt="Дождь">`,
        img_class + url + `d432.png" alt="Снег">`,
        img_class + url + `d220.png" alt="Пасмурно">`,
        img_class + url + `n220.png" alt="Пасмурно ночь">`,
    ];
    return img [index];
}


function refreshVariables() {
    multiplyScore = 1;
    selectedRow = -1;
    selectedCol = -1;
    movingItems = 0;
    gameState = "pick";
    swiped = false;
    swipeStart = null;
    modalActive = false;

}
