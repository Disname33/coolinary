$(document).ready(function () {
	windowsSet();
	newGame();

	$("#game-field").swipe({
		threshold: 10,
		tap: function (event, target) {
			if ($(target).hasClass("gem") && gameState === "pick") {
				const row = parseInt($(target).attr("id").split("_")[1]);
				const col = parseInt($(target).attr("id").split("_")[2]);
				$("#marker").show();
				$("#marker").css("top", row * GEM_SIZE + absoluteTop).css("left", col * GEM_SIZE + absoluteLeft);
				if (selectedRow === -1) {
					selectedRow = row;
					selectedCol = col;
				} else {
					if ((Math.abs(selectedRow - row) === 1 && selectedCol === col) || (Math.abs(selectedCol - col) === 1 && selectedRow === row)) {
						$("#marker").hide();
						gameState = "switch";
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
			if (swipeStart != null && gameState === "pick") {
				selectedRow = parseInt($(swipeStart).attr("id").split("_")[1]);
				selectedCol = parseInt($(swipeStart).attr("id").split("_")[2]);
				switch (direction) {
					case "up":
						if (selectedRow > 0) {
							$("#marker").hide();
							gameState = "switch";
							posX = selectedCol;
							posY = selectedRow - 1;
							gemSwitch();
						}
						break;
					case "down":
						if (selectedRow < NUM_ROWS - 1) {
							$("#marker").hide();
							gameState = "switch";
							posX = selectedCol;
							posY = selectedRow + 1;
							gemSwitch();
						}
						break;
					case "left":
						if (selectedCol > 0) {
							$("#marker").hide();
							gameState = "switch";
							posX = selectedCol - 1;
							posY = selectedRow;
							gemSwitch();
						}
						break;
					case "right":
						if (selectedCol < NUM_ROWS - 1) {
							$("#marker").hide();
							gameState = "switch";
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
				swipeStart = null;
				if ($(event.target).hasClass("gem")) {
					swipeStart = event.target;
				}
			}
		}
	})
})

function windowsSet() {
	GEM_SIZE = (window.innerWidth < (96 * NUM_COLS)) ? (window.innerWidth - 10) / NUM_COLS : 96;
	const gameField = document.getElementById('game-field');
	absoluteTop = gameField.getBoundingClientRect().top + window.scrollY;
	absoluteLeft = (window.innerWidth - (NUM_COLS * GEM_SIZE)) / 2;

	$("#game-field").css({
		"background-color": "#000000",
		"width": (NUM_COLS * GEM_SIZE) + "px",
		"height": (NUM_ROWS * GEM_SIZE) + "px"
	});
	$("#marker").css({
		"width": GEM_SIZE + "px",
		"height": GEM_SIZE + "px",
		"border": "5px solid white",
		"position": "absolute"
	}).hide();
}

function newGame() {
	restartGame(true);
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
	} else {
		document.querySelectorAll('.gem').forEach(function (element) {
			element.remove();
		});
		refreshVariables();
	}
	for (let i = 0; i < NUM_ROWS; i++) {
		for (let j = 0; j < NUM_COLS; j++) {
			do {
				jewels[i][j] = Math.floor(Math.random() * difficultly);
			} while (isStreak(i, j));
			$("#game-field").append('<div class = "' + GEM_CLASS + '" id = "' + GEM_ID_PREFIX + '_' + i + '_' + j + '"></div>');
			$("#" + GEM_ID_PREFIX + "_" + i + "_" + j).css({
				"top": (i * GEM_SIZE) + 4 + absoluteTop + "px",
				"left": (j * GEM_SIZE) + 4 + absoluteLeft + "px",
				"width": (GEM_SIZE - 10) + "px",
				"height": (GEM_SIZE - 10) + "px",
				"position": "absolute",
				"border": "1px solid white",
				"cursor": "pointer",
				"background-color": bgColors[jewels[i][j]]
			});
		}
	}
}

function checkMoving() {
	movingItems--;
	if (movingItems === 0) {
		switch (gameState) {
			case "revert":
			case "switch":
				if (!isStreak(selectedRow, selectedCol) && !isStreak(posY, posX)) {
					if (gameState !== "revert") {
						gameState = "revert";
						gemSwitch();
					} else {
						gameState = "pick";
						selectedRow = -1;
					}
				} else {

					gameState = "remove";
					if (isStreak(selectedRow, selectedCol)) {
						removeGems(selectedRow, selectedCol);
					}
					if (isStreak(posY, posX)) {
						removeGems(posY, posX);
					}
					gemFade();
					account.moves--;
					multiplyScore = 1;
				}
				break;
			case "remove":
				checkFalling();
				break;
			case "refill":
				placeNewGems();
				break;
		}
	}
}

function placeNewGems() {
	let gemsPlaced = 0;
	for (let i = 0; i < NUM_COLS; i++) {
		if (jewels[0][i] === -1) {
			jewels[0][i] = Math.floor(Math.random() * difficultly);
			$("#game-field").append('<div class = "' + GEM_CLASS + '" id = "' + GEM_ID_PREFIX + '_0_' + i + '"></div>');
			$("#" + GEM_ID_PREFIX + "_0_" + i).css({
				"top": 4 + absoluteTop + "px",
				"left": (i * GEM_SIZE) + 4 + absoluteLeft + "px",
				"width": (GEM_SIZE - 10) + "px",
				"height": (GEM_SIZE - 10) + "px",
				"position": "absolute",
				"border": "1px solid white",
				"cursor": "pointer",
				"background-color": bgColors[jewels[0][i]]
			});
			gemsPlaced++;
		}
	}
	if (gemsPlaced) {
		gameState = "remove";
		checkFalling();
	} else {
		let combo = 0
		for (let i = 0; i < NUM_ROWS; i++) {
			for (let j = 0; j < NUM_COLS; j++) {
				if (j <= NUM_COLS - 3 && jewels[i][j] === jewels[i][j + 1] && jewels[i][j] === jewels[i][j + 2]) {
					combo++;
					removeGems(i, j);
				}
				if (i <= NUM_ROWS - 3 && jewels[i][j] === jewels[i + 1][j] && jewels[i][j] === jewels[i + 2][j]) {
					combo++;
					removeGems(i, j);
				}
			}
		}
		if (combo > 0) {
			gameState = "remove";
			gemFade();
		} else {
			gameState = "pick";
			selectedRow = -1;
		}
	}
}

function checkFalling() {
	let fellDown = 0;
	for (let j = 0; j < NUM_COLS; j++) {
		for (let i = NUM_ROWS - 1; i > 0; i--) {
			if (jewels[i][j] === -1 && jewels[i - 1][j] >= 0) {
				$("#" + GEM_ID_PREFIX + "_" + (i - 1) + "_" + j).addClass("fall").attr("id", GEM_ID_PREFIX + "_" + i + "_" + j);
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
					$(this).removeClass("fall");
					checkMoving();
				}
			});
	});
	if (fellDown === 0) {
		gameState = "refill";
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

function gemSwitch() {
	const yOffset = selectedRow - posY;
	const xOffset = selectedCol - posX;
	const gemSelected = "#" + GEM_ID_PREFIX + "_" + selectedRow + "_" + selectedCol;
	const gemPos = "#" + GEM_ID_PREFIX + "_" + posY + "_" + posX;
	$(gemSelected).addClass("switch").attr("dir", "-1");
	$(gemPos).addClass("switch").attr("dir", "1");
	$.each($(".switch"), function () {
		movingItems++;
		$(this).animate({
			left: "+=" + xOffset * GEM_SIZE * $(this).attr("dir"),
			top: "+=" + yOffset * GEM_SIZE * $(this).attr("dir")
		}, {
			duration: 250,
			complete: function () {
				checkMoving();
			}
		}).removeClass("switch")
	});
	$(gemSelected).attr("id", "temp");
	$(gemPos).attr("id", GEM_ID_PREFIX + "_" + selectedRow + "_" + selectedCol);
	$("#temp").attr("id", GEM_ID_PREFIX + "_" + posY + "_" + posX);
	let temp = jewels[selectedRow][selectedCol];
	jewels[selectedRow][selectedCol] = jewels[posY][posX];
	jewels[posY][posX] = temp;

}

function removeGems(row, col) {
	const gemValue = jewels[row][col];
	let tmp = row;
	$("#" + GEM_ID_PREFIX + "_" + row + "_" + col).addClass("remove");
	if (isVerticalStreak(row, col)) {
		while (tmp > 0 && jewels[tmp - 1][col] === gemValue) {
			$("#" + GEM_ID_PREFIX + "_" + (tmp - 1) + "_" + col).addClass("remove");
			jewels[tmp - 1][col] = -1;
			tmp--;
			account.score += multiplyScore++;
		}
		tmp = row;
		while (tmp < NUM_ROWS - 1 && jewels[tmp + 1][col] === gemValue) {
			$("#" + GEM_ID_PREFIX + "_" + (tmp + 1) + "_" + col).addClass("remove");
			jewels[tmp + 1][col] = -1;
			tmp++;
			account.score += multiplyScore++;
		}
	}
	if (isHorizontalStreak(row, col)) {
		tmp = col;
		while (tmp > 0 && jewels[row][tmp - 1] === gemValue) {
			$("#" + GEM_ID_PREFIX + "_" + row + "_" + (tmp - 1)).addClass("remove");
			jewels[row][tmp - 1] = -1;
			tmp--;
			account.score += multiplyScore++;
		}
		tmp = col;
		while (tmp < NUM_COLS - 1 && jewels[row][tmp + 1] === gemValue) {
			$("#" + GEM_ID_PREFIX + "_" + row + "_" + (tmp + 1)).addClass("remove");
			jewels[row][tmp + 1] = -1;
			tmp++;
			account.score += multiplyScore++;
		}
	}
	jewels[row][col] = -1;
	account.score += multiplyScore;
}

function isVerticalStreak(row, col) {
	const gemValue = jewels[row][col];
	let streak = 0;
	let tmp = row;
	while (tmp > 0 && jewels[tmp - 1][col] === gemValue) {
		streak++;
		tmp--;
	}
	tmp = row;
	while (tmp < NUM_ROWS - 1 && jewels[tmp + 1][col] === gemValue) {
		streak++;
		tmp++;
	}
	return streak > 1
}

function isHorizontalStreak(row, col) {
	const gemValue = jewels[row][col];
	let streak = 0;
	let tmp = col;
	while (tmp > 0 && jewels[row][tmp - 1] === gemValue) {
		streak++;
		tmp--;
	}
	tmp = col;
	while (tmp < NUM_COLS - 1 && jewels[row][tmp + 1] === gemValue) {
		streak++;
		tmp++;
	}
	return streak > 1
}

function isStreak(row, col) {
	return isVerticalStreak(row, col) || isHorizontalStreak(row, col);
}
