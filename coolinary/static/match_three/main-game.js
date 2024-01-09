$(document).ready(function () {
    windowsSet();
    restartGame(true);

    $(GAME_FIELD).swipe({
        threshold: 10,
        tap: function (event, target) {
            resetIdleTimer();
            if ($(target).hasClass(GEM_CLASS) && gameState === GameStates.PICK && !modalActive) {
                const {row, col} = board.getPositionByTarget(target)
                $(MARKER).show();
                $(MARKER).css("top", row * GEM_SIZE).css("left", col * GEM_SIZE);
                if (selectedRow === -1) {
                    selectedRow = row;
                    selectedCol = col;
                } else {
                    if ((Math.abs(selectedRow - row) === 1 && selectedCol === col) || (Math.abs(selectedCol - col) === 1 && selectedRow === row)) {
                        $(MARKER).hide();
                        gameState = GameStates.SWITCH;
                        posX = col;
                        posY = row;
                        gemSwitch();
                    } else {
                        selectedRow = row;
                        selectedCol = col;
                    }
                }
            }
        },
        swipe: function (event, direction) {
            if (swipeStart != null && gameState === GameStates.PICK && !modalActive) {
                resetIdleTimer();
                const {row, col} = board.getPositionByTarget($(swipeStart));
                selectedRow = row;
                selectedCol = col;
                switch (direction) {
                    case "up":
                        if (selectedRow > 0) {
                            $(MARKER).hide();
                            gameState = GameStates.SWITCH;
                            posX = selectedCol;
                            posY = selectedRow - 1;
                            gemSwitch();
                        }
                        break;
                    case "down":
                        if (selectedRow < NUM_ROWS - 1) {
                            $(MARKER).hide();
                            gameState = GameStates.SWITCH;
                            posX = selectedCol;
                            posY = selectedRow + 1;
                            gemSwitch();
                        }
                        break;
                    case "left":
                        if (selectedCol > 0) {
                            $(MARKER).hide();
                            gameState = GameStates.SWITCH;
                            posX = selectedCol - 1;
                            posY = selectedRow;
                            gemSwitch();
                        }
                        break;
                    case "right":
                        if (selectedCol < NUM_ROWS - 1) {
                            $(MARKER).hide();
                            gameState = GameStates.SWITCH;
                            posX = selectedCol + 1;
                            posY = selectedRow;
                            gemSwitch();
                        }
                        break;
                }
            }
        },
        swipeStatus: function (event, phase) {
            if (phase === "start") {
                swipeStart = ($(event.target).hasClass(GEM_CLASS)) ? event.target : null;
            }
        }
    })
})

function windowsSet() {
    GEM_SIZE = (window.innerWidth < (96 * NUM_COLS)) ? (window.innerWidth - BORDER) / NUM_COLS : 96;
    $(GAME_FIELD).css({
        "width": (NUM_COLS * GEM_SIZE) + BORDER + "px",
        "height": (NUM_ROWS * GEM_SIZE) + BORDER + "px",
    });
    $(MARKER).css({
        "width": BORDER + GEM_SIZE + "px",
        "height": BORDER + GEM_SIZE + "px",
    }).hide();

}

function restartGame(firstStart = false) {

    account.score = 0;
    account.moves = 20;
    account.target = accountValues.target;
    account.level = accountValues.level;
    if (firstStart) {
        board = new Board();
        startIdleTimer();
    } else {
        refreshVariables();
        resetIdleTimer()
        board.initialize();
    }

}

function checkMoving() {
    movingItems--;
    if (movingItems === 0) {
        switch (gameState) {
            case GameStates.REVERT:
            case GameStates.SWITCH:
                if (Gem.is_rainbow(selectedRow, selectedCol) || Gem.is_rainbow(posY, posX)) {
                    if (Gem.is_rainbow(selectedRow, selectedCol)) {
                        removeColor(posY, posX, selectedRow, selectedCol);
                    }
                    if (Gem.is_rainbow(posY, posX)) {
                        removeColor(selectedRow, selectedCol, posY, posX);
                    }
                    afterAction()
                } else if (Gem.is_double_flash(selectedRow, selectedCol) && Gem.is_double_flash(posY, posX)) {
                    if (selectedRow > 0) removeRow(selectedRow - 1);
                    removeRow(selectedRow);
                    if (selectedRow < NUM_ROWS) removeRow(selectedRow + 1);
                    if (selectedCol > 0) removeCol(selectedCol - 1);
                    removeCol(selectedCol);
                    if (selectedCol < NUM_COLS) removeCol(selectedCol + 1);
                    afterAction()
                } else if ((Gem.is_double_flash(selectedRow, selectedCol) && Gem.is_line_flash(posY, posX)) || ((Gem.is_line_flash(selectedRow, selectedCol) && Gem.is_double_flash(posY, posX)))) {
                    removeRow(selectedRow);
                    removeRow(posY);
                    removeCol(selectedCol);
                    removeCol(posX);
                    afterAction()
                } else if (Gem.is_line_flash(selectedRow, selectedCol) && Gem.is_line_flash(posY, posX)) {
                    removeRow(selectedRow);
                    removeCol(selectedCol);
                    afterAction()
                } else if (board.isStreak(selectedRow, selectedCol) || board.isStreak(posY, posX)) {
                    if (board.isStreak(selectedRow, selectedCol)) {
                        removeGems(selectedRow, selectedCol);
                    }
                    if (board.isStreak(posY, posX)) {
                        removeGems(posY, posX);
                    }
                    afterAction()
                } else if (gameState !== GameStates.REVERT) {
                    gameState = GameStates.REVERT;
                    gemSwitch();
                } else if (!checkingForMoves().length) {
                    shuffleGems();
                } else {
                    gameState = GameStates.PICK;
                    selectedRow = -1;
                }
                break;
            case GameStates.REMOVE:
                checkFalling();
                break;
            case GameStates.REFILL:
                placeNewGems();
                break;
            case GameStates.PICK:
                if (!checkingForMoves().length) setTimeout(shuffleGems, 500)
                break
        }
    }
}

function afterAction() {
    account.moves--;
    multiplyScore = 1;
    gameState = GameStates.REMOVE;
    gemFade();
}

function removeColor(row, col, rainbow_row, rainbow_col) {
    const gemClass = Gem.getElementByID(row, col).classList[1];
    const gem = new Gem(board.grid[row][col].value);
    for (let i = 0; i < NUM_ROWS; i++) {
        for (let j = 0; j < NUM_COLS; j++) {
            if (board.grid[i][j].equals(gem)) {
                Gem.getElementByID(i, j).classList.add(gemClass);

                flash_explode(i, j);
                board.grid[i][j].forDel();
            }
        }
    }
    flash_explode(rainbow_row, rainbow_col)
    board.grid[rainbow_row][rainbow_col].forDel()
}

function placeNewGems() {
    let gemsPlaced = 0;
    for (let i = 0; i < NUM_COLS; i++) {
        if (!board.inGame(0, i)) {
            board.grid[0][i] = new Gem();
            board.createGemDiv(0, i);
            gemsPlaced++;
        }
    }
    if (gemsPlaced) {
        gameState = GameStates.REMOVE;
        checkFalling();
    } else {
        findCombos()
    }
}

function findCombos() {
    let combo = 0;
    for (let i = 0; i < NUM_ROWS; i++) {
        for (let j = 0; j < NUM_COLS; j++) {
            let double = false
            const h_streak = board.horizontalStreak(i, j)
            const v_streak = board.verticalStreak(i, j)
            for (let v_row of v_streak) {
                if (board.horizontalStreak(v_row, j).length) {
                    combo++;
                    removeGems(v_row, j);
                    double = true
                    break;
                }
            }
            for (let h_col of h_streak) {
                if (board.verticalStreak(i, h_col).length) {
                    combo++;
                    removeGems(i, h_col);
                    double = true
                    break;
                }
            }
            if (!double && (h_streak.length || v_streak.length)) {
                combo++;
                removeGems(i, j);
            }
        }
    }
    if (combo > 0) {
        gameState = GameStates.REMOVE;
        gemFade();
    } else if (!checkingForMoves().length) {
        setTimeout(shuffleGems, 500)
    } else {
        gameState = GameStates.PICK;
        selectedRow = -1;
    }
}

function checkFalling() {
    let fellDown = 0;
    let temp;
    for (let j = 0; j < NUM_COLS; j++) {
        for (let i = NUM_ROWS - 1; i > 0; i--) {
            if (!board.inGame(i, j) && board.inGame(i - 1, j)) {
                $("#" + Gem.getID(i - 1, j)).addClass(GameStates.FALL).attr("id", Gem.getID(i, j));
                temp = board.grid[i][j];
                board.grid[i][j] = board.grid[i - 1][j];
                board.grid[i - 1][j] = temp;
                fellDown++;
            }
        }
    }
    $.each($(".fall"), function () {
        movingItems++;
        $(this).animate({
                top: "+=" + GEM_SIZE
            },
            {
                duration: 100,
                complete: function () {
                    $(this).removeClass(GameStates.FALL);
                    checkMoving();
                }
            });
    });
    if (!fellDown) {
        gameState = GameStates.REFILL;
        movingItems = 1;
        checkMoving();
    }
}

function gemFade() {
    $.each($(".remove"), function () {
        movingItems++;
        $(this).animate({
                opacity: 0
            },
            {
                duration: 200,
                complete: function () {
                    $(this).remove();
                    checkMoving();
                }
            });
    });
}

function gemSwitch(row = selectedRow, col = selectedCol, row2 = posY, col2 = posX, check_moving = true) {
    const yOffset = row - row2;
    const xOffset = col - col2;
    const gemSelected = "#" + Gem.getID(row, col);
    const gemPos = "#" + Gem.getID(row2, col2);
    $(gemSelected).addClass(GameStates.SWITCH).attr("dir", "-1");
    $(gemPos).addClass(GameStates.SWITCH).attr("dir", "1");
    $.each($(".switch"), function () {
        if (check_moving) movingItems++;
        $(this).animate({
            left: "+=" + xOffset * GEM_SIZE * $(this).attr("dir"),
            top: "+=" + yOffset * GEM_SIZE * $(this).attr("dir")
        }, {
            duration: 250,
            complete: function () {
                if (check_moving) checkMoving();
            }
        }).removeClass(GameStates.SWITCH)
    });
    $(gemSelected).attr("id", "temp");
    $(gemPos).attr("id", Gem.getID(row, col));
    $("#temp").attr("id", Gem.getID(row2, col2));
    const temp = board.grid[row][col];
    board.grid[row][col] = board.grid[row2][col2];
    board.grid[row2][col2] = temp;
}

function removeGems(row, col) {
    const v_streak = board.verticalStreak(row, col);
    const h_streak = board.horizontalStreak(row, col);
    const gemElement = $("#" + Gem.getID(row, col));
    const copyGem = board.grid[row][col].copy();
    if (board.inGame(row, col)) {
        let flash_str = flash_explode(row, col);
        for (let v_row of v_streak) {
            flash_str = flash_explode(v_row, col);
            if (flash_str === Flash.DOUBLE || flash_str === Flash.VERTICAL) {
                break;
            }
        }
        for (let h_col of h_streak) {
            flash_str = flash_explode(row, h_col);
            if (flash_str === Flash.DOUBLE || flash_str === Flash.HORIZONTAL) {
                break;
            }
        }
        account.score += multiplyScore;
        if (v_streak.length > 3 || h_streak.length > 3) {
            copyGem.flash = Flash.RAINBOW;
        } else if (v_streak.length && h_streak.length) {
            copyGem.flash = Flash.DOUBLE;
        } else if (h_streak.length > 2) {
            copyGem.flash = Flash.HORIZONTAL;
        } else if (v_streak.length > 2) {
            copyGem.flash = Flash.VERTICAL;
        } else {
            copyGem.flash = '';
        }
        if (copyGem.flash !== '') {
            gemElement.remove();
            board.grid[row][col] = copyGem;
            board.createGemDiv(row, col);
        }

    }
}

function flash_explode(row, col, del_self = true) {
    let flash_str = ''
    const gemElement = Gem.getElementByID(row, col);
    if (gemElement !== null && board.inGame(row, col)) {
        if (Gem.is_rainbow(row, col)) {
            removeGem(row, col)
            const gemValue = Math.floor(Math.random() * difficulty);
            for (let i = 0; i < NUM_ROWS; i++) {
                for (let j = 0; j < NUM_COLS; j++) {
                    if (board.grid[i][j].value === gemValue) {
                        flash_explode(i, j);
                        board.grid[i][j].forDel();
                    }
                }
            }
            account.score += 150;
        } else if (Gem.is_double_flash(row, col)) {
            removeGem(row, col)
            removeRow(row);
            removeCol(col);
            flash_str = Flash.DOUBLE
        } else if (gemElement.classList.contains(Flash.HORIZONTAL)) {
            removeGem(row, col)
            removeRow(row);
            flash_str = Flash.HORIZONTAL
        } else if (gemElement.classList.contains(Flash.VERTICAL)) {
            removeGem(row, col)
            removeCol(col);
            flash_str = Flash.VERTICAL
        } else if (del_self) {
            removeGem(row, col)
        }
    }
    return flash_str
}

function removeGem(row, col) {
    $("#" + Gem.getID(row, col)).addClass(GameStates.REMOVE);
    board.grid[row][col].forDel();
    account.score += multiplyScore++;
}

function removeRow(row) {
    for (let i = 0; i < NUM_COLS; i++) {
        flash_explode(row, i)
    }
    account.score += 30;
}

function removeCol(col) {
    for (let i = 0; i < NUM_ROWS; i++) {
        flash_explode(i, col)
    }
    account.score += 30;
}

function shuffleGems() {
    for (let row = 0; row < NUM_ROWS; row++) {
        for (let col = 0; col < NUM_COLS; col++) {
            if (board.inGame(row, col)) {
                let row2, col2;
                do {
                    row2 = Math.floor(Math.random() * NUM_ROWS);
                    col2 = Math.floor(Math.random() * NUM_COLS);
                } while (!board.inGame(row2, col2))
                gemSwitch(row, col, row2, col2, false)
            }
        }
    }
    setTimeout(findCombos, 250);
}

function checkingForMoves() {
    let gem;
    for (let i = 0; i < NUM_ROWS; i++) {
        for (let j = 0; j < NUM_COLS; j++) {
            gem = board.grid[i][j];
            if (j < NUM_COLS - 1) {
                if (Gem.is_flash(i, j) && Gem.is_flash(i, j + 1)) return [i, j];
                if (j < NUM_COLS - 2) {
                    if (i < NUM_ROWS - 1) {
                        if (gem.equals(board.grid[i + 1][j + 1]) && gem.equals(board.grid[i][j + 2])) {
                            return [i + 1, j + 1];
                        } else if (gem.equals(board.grid[i][j + 1]) && gem.equals(board.grid[i + 1][j + 2])) {
                            return [i + 1, j + 2];
                        } else if (gem.equals(board.grid[i + 1][j + 1]) && gem.equals(board.grid[i + 1][j + 2])) {
                            return [i, j];
                        }
                    }
                    if (i > 0) {
                        if (gem.equals(board.grid[i - 1][j + 1]) && gem.equals(board.grid[i][j + 2])) {
                            return [i - 1, j + 1];
                        } else if (gem.equals(board.grid[i][j + 1]) && gem.equals(board.grid[i - 1][j + 2])) {
                            return [i - 1, j + 2];
                        } else if (gem.equals(board.grid[i - 1][j + 1]) && gem.equals(board.grid[i - 1][j + 2])) {
                            return [i, j];
                        }
                    }
                    if (j < NUM_COLS - 3) {
                        if (gem.equals(board.grid[i][j + 1]) && gem.equals(board.grid[i][j + 3])) {
                            return [i, j + 3];
                        } else if (gem.equals(board.grid[i][j + 2]) && gem.equals(board.grid[i][j + 3])) {
                            return [i, j];
                        }
                    }
                }
            }
            if (i < NUM_ROWS - 1) {
                if (Gem.is_flash(i, j) && Gem.is_flash(i + 1, j)) return [i, j];
                if (i < NUM_ROWS - 2) {
                    if (j > 0) {
                        if (gem.equals(board.grid[i + 1][j - 1]) && gem.equals(board.grid[i + 2][j])) {
                            return [i + 1, j - 1];
                        } else if (gem.equals(board.grid[i + 1][j]) && gem.equals(board.grid[i + 2][j - 1])) {
                            return [i + 2, j - 1];
                        } else if (gem.equals(board.grid[i + 1][j - 1]) && gem.equals(board.grid[i + 2][j - 1])) {
                            return [i, j];
                        }
                    }
                    if (j < NUM_COLS - 1) {
                        if (gem.equals(board.grid[i + 1][j + 1]) && gem.equals(board.grid[i + 2][j])) {
                            return [i + 1, j + 1];
                        } else if (gem.equals(board.grid[i + 1][j]) && gem.equals(board.grid[i + 2][j + 1])) {
                            return [i + 2, j + 1];
                        } else if (gem.equals(board.grid[i + 1][j + 1]) && gem.equals(board.grid[i + 2][j + 1])) {
                            return [i, j];
                        }
                    }
                    if (i < NUM_ROWS - 3) {
                        if (gem.equals(board.grid[i + 1][j]) && gem.equals(board.grid[i + 3][j])) {
                            return [i + 3, j];
                        } else if (gem.equals(board.grid[i + 2][j]) && gem.equals(board.grid[i + 3][j])) {
                            return [i, j];
                        }
                    }
                }
            }
            if (Gem.is_rainbow(i, j)) return [i, j];
        }
    }
    return []
}

function setMarkerInMovable() {
    const position = checkingForMoves()
    if (position.length) {
        $(MARKER).show();
        $(MARKER).css("top", position[0] * GEM_SIZE).css("left", position[1] * GEM_SIZE);
        $(MARKER).addClass('blinking-element');
        setTimeout(function () {
            $(MARKER).removeClass('blinking-element');
            $(MARKER).hide();
        }, 4000);
    }

}

function startIdleTimer() {
    idleTimeout = setInterval(setMarkerInMovable, 12000);
}

function resetIdleTimer() {
    clearInterval(idleTimeout);
    startIdleTimer();
}

document.addEventListener('click', resetIdleTimer);