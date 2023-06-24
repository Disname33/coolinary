$(document).ready(function () {
	windowsSet();
	restartGame(true);

	$(GAME_FIELD).swipe({
		threshold: 10,
		tap: function (event, target) {
			resetIdleTimer();
			if ($(target).hasClass(GEM_CLASS) && gameState === GameStates.PICK && !modalActive) {
				const row = parseInt($(target).attr("id").split("_")[1]);
				const col = parseInt($(target).attr("id").split("_")[2]);
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
				const position = $(swipeStart).attr("id").split("_");
				selectedRow = parseInt(position[1]);
				selectedCol = parseInt(position[2]);
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
		// "background-color": "#000000",
		"width": (NUM_COLS * GEM_SIZE) + BORDER + "px",
		"height": (NUM_ROWS * GEM_SIZE) + BORDER + "px",
		"position": "relative"
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
		for (let i = 0; i < NUM_ROWS; i++) {
			jewels[i] = [];
			for (let j = 0; j < NUM_COLS; j++) {
				jewels[i][j] = -1;
			}
		}
		startIdleTimer();
	} else {
		document.querySelectorAll('.gem').forEach(function (element) {
			element.remove();
		});
		refreshVariables();
		resetIdleTimer()
	}
	for (let i = 0; i < NUM_ROWS; i++) {
		for (let j = 0; j < NUM_COLS; j++) {
			do {
				jewels[i][j] = Math.floor(Math.random() * difficultly);
			} while (isStreak(i, j));
			createGemDiv(i, j);
		}
	}

}

function checkMoving() {
	movingItems--;
	if (movingItems === 0) {
		if (!checkingForMoves().length) shuffleJewels();
		switch (gameState) {
			case GameStates.REVERT:
			case GameStates.SWITCH:
				if (is_rainbow(selectedRow, selectedCol) || is_rainbow(posY, posX)) {
					if (is_rainbow(selectedRow, selectedCol)) {
						removeColor(posY, posX, selectedRow, selectedCol);
					}
					if (is_rainbow(posY, posX)) {
						removeColor(selectedRow, selectedCol, posY, posX);
					}
					afterAction()
				} else if (is_double_flash(selectedRow, selectedCol) && is_double_flash(posY, posX)) {
					if (selectedRow > 0) removeRow(selectedRow - 1);
					removeRow(selectedRow);
					if (selectedRow < NUM_ROWS) removeRow(selectedRow + 1);
					if (selectedCol > 0) removeCol(selectedCol - 1);
					removeCol(selectedCol);
					if (selectedCol < NUM_COLS) removeCol(selectedCol + 1);
					afterAction()
				} else if ((is_double_flash(selectedRow, selectedCol) && is_line_flash(posY, posX)) || ((is_line_flash(selectedRow, selectedCol) && is_double_flash(posY, posX)))) {
					removeRow(selectedRow);
					removeRow(posY);
					removeCol(selectedCol);
					removeCol(posX);
					afterAction()
				} else if (is_line_flash(selectedRow, selectedCol) && is_line_flash(posY, posX)) {
					removeRow(selectedRow);
					removeCol(selectedCol);
					afterAction()
				} else if (isStreak(selectedRow, selectedCol) || isStreak(posY, posX)) {
					if (isStreak(selectedRow, selectedCol)) {
						removeGems(selectedRow, selectedCol);
					}
					if (isStreak(posY, posX)) {
						removeGems(posY, posX);
					}
					afterAction()
				} else if (gameState !== GameStates.REVERT) {
					gameState = GameStates.REVERT;
					gemSwitch();
				} else if (!checkingForMoves().length) {
					shuffleJewels();
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
				if (!checkingForMoves().length) shuffleJewels();
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

function is_flash(row, col) {
	const gem = document.getElementById(getGemID(row, col));
	if (gem !== null) {
		return gem.classList.contains(Flash.HORIZONTAL) || gem.classList.contains(Flash.VERTICAL) || gem.classList.contains(Flash.DOUBLE) || gem.classList.contains(Flash.RAINBOW);
	} else return false
}

function is_line_flash(row, col) {
	const gem = document.getElementById(getGemID(row, col));
	if (gem !== null) {
		return gem.classList.contains(Flash.HORIZONTAL) || gem.classList.contains(Flash.VERTICAL);
	} else return false
}

function is_double_flash(row, col) {
	const gem = document.getElementById(getGemID(row, col));
	if (gem !== null) {
		return gem.classList.contains(Flash.DOUBLE);
	} else return false
}

function is_rainbow(row, col) {
	const gem = document.getElementById(getGemID(row, col));
	if (gem !== null) {
		return gem.classList.contains(Flash.RAINBOW);
	} else return false
}

function removeColor(row, col, rainbow_row, rainbow_col) {
	const gemClass = document.getElementById(getGemID(row, col)).classList[1];
	const gemValue = jewels[row][col];
	for (let i = 0; i < NUM_ROWS; i++) {
		for (let j = 0; j < NUM_COLS; j++) {
			if (jewels[i][j] === gemValue) {
				document.getElementById(getGemID(i, j)).classList.add(gemClass);
				flash_explode(i, j);
				jewels[i][j] = -1;
			}
		}
	}
	flash_explode(rainbow_row, rainbow_col)
	jewels[rainbow_row][rainbow_col] = -1
}

function createGemDiv(row, col) {
	$(GAME_FIELD).append('<div class = "' + GEM_CLASS + '" id = "' + getGemID(row, col) + `">` + getImg(jewels[row][col]) + `</div>`);
	$("#" + getGemID(row, col)).css({
		"top": (row * GEM_SIZE) + BORDER + "px",
		"left": (col * GEM_SIZE) + BORDER + "px",
		"width": (GEM_SIZE - BORDER) + "px",
		"height": (GEM_SIZE - BORDER) + "px",
		"background-color": bgColors[jewels[row][col]]
	});
}

function placeNewGems() {
	let gemsPlaced = 0;
	for (let i = 0; i < NUM_COLS; i++) {
		if (jewels[0][i] === -1) {
			jewels[0][i] = Math.floor(Math.random() * difficultly);
			createGemDiv(0, i);
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
			const h_streak = horizontalStreak(i, j)
			const v_streak = verticalStreak(i, j)
			for (let v_row of v_streak) {
				if (horizontalStreak(v_row, j).length) {
					combo++;
					removeGems(v_row, j);
					double = true
					break;
				}
			}
			for (let h_col of h_streak) {
				if (verticalStreak(i, h_col).length) {
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
	} else {
		gameState = GameStates.PICK;
		selectedRow = -1;
	}
}


function checkFalling() {
	let fellDown = 0;
	for (let j = 0; j < NUM_COLS; j++) {
		for (let i = NUM_ROWS - 1; i > 0; i--) {
			if (jewels[i][j] === -1 && jewels[i - 1][j] >= 0) {
				$("#" + getGemID(i - 1, j)).addClass(GameStates.FALL).attr("id", getGemID(i, j));
				jewels[i][j] = jewels[i - 1][j];
				jewels[i - 1][j] = -1;
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
	if (fellDown === 0) {
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
	const gemSelected = "#" + getGemID(row, col);
	const gemPos = "#" + getGemID(row2, col2);
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
	$(gemPos).attr("id", getGemID(row, col));
	$("#temp").attr("id", getGemID(row2, col2));
	let temp = jewels[row][col];
	jewels[row][col] = jewels[row2][col2];
	jewels[row2][col2] = temp;
}

function removeGems(row, col) {
	const gemValue = jewels[row][col];
	const v_streak = verticalStreak(row, col)
	const h_streak = horizontalStreak(row, col)
	const gem = $("#" + getGemID(row, col))
	let flash_str = flash_explode(row, col, false);
	if (gemValue !== -1) {
		if (v_streak.length > 3 || h_streak.length > 3) {
			gem.addClass(Flash.RAINBOW);
		} else if (v_streak.length && h_streak.length) {
			gem.addClass(Flash.DOUBLE);
		} else if (h_streak.length > 2) {
			gem.addClass(Flash.HORIZONTAL);
		} else if (v_streak.length > 2) {
			gem.addClass(Flash.VERTICAL);
		} else {
			flash_explode(row, col);
		}
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
	}
}

function flash_explode(row, col, del_self = true) {
	let flash_str = ''
	const gem = document.getElementById(getGemID(row, col));
	if (gem !== null && jewels[row][col] !== -1) {
		if (is_rainbow(row, col)) {
			removeGem(row, col)
			const gemValue = Math.floor(Math.random() * difficultly);
			for (let i = 0; i < NUM_ROWS; i++) {
				for (let j = 0; j < NUM_COLS; j++) {
					if (jewels[i][j] === gemValue) {
						flash_explode(i, j);
						jewels[i][j] = -1;
					}
				}
			}
			account.score += 150;
		} else if (is_double_flash(row, col)) {
			removeGem(row, col)
			removeRow(row);
			removeCol(col);
			flash_str = Flash.DOUBLE
		} else if (gem.classList.contains(Flash.HORIZONTAL)) {
			removeGem(row, col)
			removeRow(row);
			flash_str = Flash.HORIZONTAL
		} else if (gem.classList.contains(Flash.VERTICAL)) {
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
	$("#" + getGemID(row, col)).addClass(GameStates.REMOVE);
	jewels[row][col] = -1;
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

function verticalStreak(row, col) {
	const gemValue = jewels[row][col];
	let streak = [];
	let tmp = row;
	while (tmp > 0 && jewels[tmp - 1][col] === gemValue) {
		streak.push(tmp - 1);
		tmp--;
	}
	tmp = row;
	while (tmp < NUM_ROWS - 1 && jewels[tmp + 1][col] === gemValue) {
		streak.push(tmp + 1);
		tmp++;
	}
	return streak.length > 1 ? streak : []
}

function horizontalStreak(row, col) {
	const gemValue = jewels[row][col];
	let streak = [];
	let tmp = col;
	while (tmp > 0 && jewels[row][tmp - 1] === gemValue) {
		streak.push(tmp - 1);
		tmp--;
	}
	tmp = col;
	while (tmp < NUM_COLS - 1 && jewels[row][tmp + 1] === gemValue) {
		streak.push(tmp + 1);
		tmp++;
	}
	return streak.length > 1 ? streak : []
}

function isStreak(row, col) {
	return verticalStreak(row, col).length || horizontalStreak(row, col).length;
}

function getGemID(row, col) {
	return GEM_ID_PREFIX + "_" + row + "_" + col;
}

function checkingForMoves() {
	let jewel;
	for (let i = 0; i < NUM_ROWS; i++) {
		for (let j = 0; j < NUM_COLS; j++) {
			jewel = jewels[i][j];
			if (j < NUM_COLS - 1) {
				if (is_flash(i, j) && is_flash(i, j + 1)) return [i, j];
				if (j < NUM_COLS - 2) {
					if (i < NUM_ROWS - 1) {
						if (jewel === jewels[i + 1][j + 1] && jewel === jewels[i][j + 2]) {
							return [i + 1, j + 1];
						} else if (jewel === jewels[i][j + 1] && jewel === jewels[i + 1][j + 2]) {
							return [i + 1, j + 2];
						} else if (jewel === jewels[i + 1][j + 1] && jewel === jewels[i + 1][j + 2]) {
							return [i, j];
						}
					}
					if (i > 0) {
						if (jewel === jewels[i - 1][j + 1] && jewel === jewels[i][j + 2]) {
							return [i - 1, j + 1];
						} else if (jewel === jewels[i][j + 1] && jewel === jewels[i - 1][j + 2]) {
							return [i - 1, j + 2];
						} else if (jewel === jewels[i - 1][j + 1] && jewel === jewels[i - 1][j + 2]) {
							return [i, j];
						}
					}
					if (j < NUM_COLS - 3) {
						if (jewel === jewels[i][j + 1] && jewel === jewels[i][j + 3]) {
							return [i, j + 3];
						} else if (jewel === jewels[i][j + 2] && jewel === jewels[i][j + 3]) {
							return [i, j];
						}
					}
				}
			}
			if (i < NUM_ROWS - 1) {
				if (is_flash(i, j) && is_flash(i + 1, j)) return [i, j];
				if (i < NUM_ROWS - 2) {
					if (j > 0) {
						if (jewel === jewels[i + 1][j - 1] && jewel === jewels[i + 2][j]) {
							return [i + 1, j - 1];
						} else if (jewel === jewels[i + 1][j] && jewel === jewels[i + 2][j - 1]) {
							return [i + 2, j - 1];
						} else if (jewel === jewels[i + 1][j - 1] && jewel === jewels[i + 2][j - 1]) {
							return [i, j];
						}
					}
					if (j < NUM_COLS - 1) {
						if (jewel === jewels[i + 1][j + 1] && jewel === jewels[i + 2][j]) {
							return [i + 1, j + 1];
						} else if (jewel === jewels[i + 1][j] && jewel === jewels[i + 2][j + 1]) {
							return [i + 2, j + 1];
						} else if (jewel === jewels[i + 1][j + 1] && jewel === jewels[i + 2][j + 1]) {
							return [i, j];
						}
					}
					if (i < NUM_ROWS - 3) {
						if (jewel === jewels[i + 1][j] && jewel === jewels[i + 3][j]) {
							return [i + 3, j];
						} else if (jewel === jewels[i + 2][j] && jewel === jewels[i + 3][j]) {
							return [i, j];
						}
					}
				}
			}
			if (is_rainbow(i, j)) return [i, j];
		}
	}
	return []
}

function shuffleJewels() {
	for (let row = 0; row < NUM_ROWS; row++) {
		for (let col = 0; col < NUM_COLS; col++) {
			const row2 = Math.floor(Math.random() * NUM_ROWS);
			const col2 = Math.floor(Math.random() * NUM_COLS);
			gemSwitch(row, col, row2, col2, false)
		}
	}
	setTimeout(findCombos, 250);
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