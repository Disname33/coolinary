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
let absoluteTop = 0;
let absoluteLeft = (window.innerWidth - (NUM_COLS * GEM_SIZE)) / 2;
let selectedRow = -1;
let selectedCol = -1;
let jewels = [];
let movingItems = 0;
let gameState = "pick";
let swiped = false;
let swipeStart = null;
let multiplyScore = 1;
const levelDifficultly = [3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 8, 8]

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
