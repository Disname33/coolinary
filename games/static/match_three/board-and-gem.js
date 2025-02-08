class Board {
    grid = [];
    flashRemoveQueue = [];
    newGemQueue = [];

    constructor(map = Array(NUM_ROWS).fill(Array(NUM_COLS).fill(-1))) {
        if (Board.instance) {
            return Board.instance;
        }
        this.initialize(map);
        Board.instance = this;
    }

    initialize(map = Array(NUM_ROWS).fill(Array(NUM_COLS).fill(-1))) {
        this.clear()
        this.grid = [];
        for (let row = 0; row < NUM_ROWS; row++) {
            this.grid[row] = [];
            for (let col = 0; col < NUM_COLS; col++) {
                if (map[row][col] === -1) {
                    let count = 0; // для защиты от зацикливаний на кривой карте
                    do {
                        this.grid[row][col] = new Gem();
                        count++
                    } while (this.isStreak(row, col) || count < 10);
                } else {
                    this.grid[row][col] = new Gem(map[row][col]);
                }
                this.createGemDiv(row, col);
            }
        }
    }

    addFlashToRemove(row, col) {
        let gem = this.grid[row][col];
        gem.row = row;
        gem.col = col;
        this.flashRemoveQueue.push(gem)
    }

    addNewFlashGemAtQueue(gem, row, col) {
        gem.row = row;
        gem.col = col;
        this.newGemQueue.push(gem)
    }

    addNewFlashGemAtBoard() {
        while (this.newGemQueue.length) {
            let gem = this.newGemQueue.pop();
            $("#" + Gem.getID(gem.row, gem.col)).remove();
            this.grid[gem.row][gem.col] = gem;
            this.createGemDiv(gem.row, gem.col);
        }
    }

    createGemDiv(row, col) {
        const gem = this.grid[row][col];
        $(GAME_FIELD).append('<div class = "' + GEM_CLASS + ' ' + gem.flash + '" id = "' + Gem.getID(row, col) + `">` + getImg(gem.value) + `</div>`);
        $("#" + Gem.getID(row, col)).css({
            "top": (row * GEM_SIZE) + BORDER + "px",
            "left": (col * GEM_SIZE) + BORDER + "px",
            "width": (GEM_SIZE - BORDER) + "px",
            "height": (GEM_SIZE - BORDER) + "px",
            "background-color": bgColors[gem.value]
        });
    }

    createBeamDiv(row, col, type) {
        let boardWidth = $(GAME_FIELD).width();
        if (type === Flash.HORIZONTAL || type === Flash.DOUBLE) {
            let beamId = 'beam_' + Flash.HORIZONTAL + '_' + row + '_' + col;
            $(GAME_FIELD).append('<div class = "beam" id = "' + beamId + `"></div>`);

            $("#" + beamId).css({
                "top": (row * GEM_SIZE) + BORDER + "px",
                "left": ((col + 0.5) * GEM_SIZE) + BORDER - boardWidth + "px",
                "width": (boardWidth * 2) + "px",
                "height": (GEM_SIZE - BORDER) + "px",
            });
            setTimeout(() => {
                $("#" + beamId).remove()
            }, 1000);
        }
        if (type === Flash.VERTICAL || type === Flash.DOUBLE) {
            let beamId = 'beam_' + Flash.VERTICAL + '_' + row + '_' + col;
            $(GAME_FIELD).append('<div class = "beam rotate90" id = "' + beamId + `"></div>`);
            let boardHeight = $(GAME_FIELD).height();
            $("#" + beamId).css({
                "top": (row * GEM_SIZE) + BORDER + "px",
                "left": ((col + 1.5) * GEM_SIZE) + BORDER - boardWidth + "px",
                "height": (GEM_SIZE - BORDER) + "px",
                "width": (boardHeight * 2) + "px"
            });
            setTimeout(() => {
                $("#" + beamId).remove()
            }, 1000);
        }
    }

    clear() {
        document.querySelectorAll('.gem').forEach(function (element) {
            element.remove();
        });
    }


    getPositionByTarget(target) {
        const position = $(target).attr("id").split("_");
        return {row: parseInt(position[1]), col: parseInt(position[2])}
    }

    inGame(row, col) {
        return this.grid[row][col].inGame();
    }

    verticalStreak(row, col) {
        const gem = this.grid[row][col];
        let streak = [];
        let tmp = row;
        while (tmp > 0 && this.grid[tmp - 1][col].equals(gem)) {
            streak.push(tmp - 1);
            tmp--;
        }
        tmp = row;
        while (tmp < NUM_ROWS - 1 && this.grid.length > tmp + 1 && this.grid[tmp + 1][col].equals(gem)) {
            streak.push(tmp + 1);
            tmp++;
        }
        return streak.length > 1 ? streak : []
    }

    horizontalStreak(row, col) {
        const gem = this.grid[row][col];
        let streak = [];
        let tmp = col;
        while (tmp > 0 && this.grid[row][tmp - 1].equals(gem)) {
            streak.push(tmp - 1);
            tmp--;
        }
        tmp = col;
        while (tmp < NUM_COLS - 1 && this.grid[row].length > tmp + 1 && this.grid[row][tmp + 1].equals(gem)) {
            streak.push(tmp + 1);
            tmp++;
        }
        return streak.length > 1 ? streak : []
    }

    isStreak(row, col) {
        return this.verticalStreak(row, col).length || this.horizontalStreak(row, col).length;
    }
}


class Gem {
    col;
    row;

    constructor(value = Math.floor(Math.random() * difficulty), type = GEM_CLASS, flash = '') {
        this.value = value;
        this.type = type;
        this.flash = flash;
    }

    static getID(row, col) {
        return GEM_ID_PREFIX + "_" + row + "_" + col;
    }

    static getElementByID(row, col) {
        return document.getElementById(Gem.getID(row, col));
    }

    static is_flash(row, col) {
        const gem = Gem.getElementByID(row, col);
        if (gem !== null) {
            return gem.classList.contains(Flash.HORIZONTAL) || gem.classList.contains(Flash.VERTICAL) || gem.classList.contains(Flash.DOUBLE) || gem.classList.contains(Flash.RAINBOW);
        } else return false
    }

    static is_line_flash(row, col) {
        const gem = Gem.getElementByID(row, col);
        if (gem !== null) {
            return gem.classList.contains(Flash.HORIZONTAL) || gem.classList.contains(Flash.VERTICAL);
        } else return false
    }

    static is_double_flash(row, col) {
        const gem = Gem.getElementByID(row, col);
        if (gem !== null) {
            return gem.classList.contains(Flash.DOUBLE);
        } else return false
    }

    static is_rainbow(row, col) {
        const gem = Gem.getElementByID(row, col);
        if (gem !== null) {
            return gem.classList.contains(Flash.RAINBOW);
        } else return false
    }

    copy() {
        return new Gem(this.value, this.type, this.flash)
    }

    addClass(newClass) {
        this.class += " " + newClass;
    }

    forDel() {
        this.value = -1;
    }

    equals(other) {
        return this.value === other.value;
    }

    inGame() {
        // return this.value > -1 && this.type === GEM_CLASS;
        return this.value !== -1;
    }


}

class Cell {
    constructor(row, col) {
        this.row = row;
        this.col = col;
    }
}