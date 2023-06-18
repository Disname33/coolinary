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
    const img_class = `class = "img-fluid pointer-events"`
    const img = [
        `<img ` + img_class + ` src="` + url + `d440.png" alt="Гроза">`,
        `<img  ` + img_class + ` src="` + url + `n000.png" alt="Месяц">`,
        `<img  ` + img_class + ` src="` + url + `d000.png" alt="Солнце">`,
        `<img  ` + img_class + ` src="` + url + `d400.png" alt="Тучи">`,
        `<img  ` + img_class + ` src="` + url + `d430.png" alt="Дождь">`,
        `<img  ` + img_class + ` src="` + url + `d432.png" alt="Снег">`,
        `<img  ` + img_class + ` src="` + url + `d220.png" alt="Пасмурно">`,
        `<img  ` + img_class + ` src="` + url + `n220.png" alt="Пасмурно ночь">`,
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
