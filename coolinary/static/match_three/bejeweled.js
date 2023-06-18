$(document).ready(function () {
	windowsSet();
	restartGame(true);

	$("#game-field").swipe({
		threshold: 10,
		tap: function (event, target) {
			if ($(target).hasClass("gem") && gameState === "pick" && !modalActive) {
				const row = parseInt($(target).attr("id").split("_")[1]);
				const col = parseInt($(target).attr("id").split("_")[2]);
				$("#marker").show();
				$('#marker').css("top", row * GEM_SIZE).css("left", col * GEM_SIZE);
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
			if (swipeStart != null && gameState === "pick" && !modalActive) {
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
				swipeStart = ($(event.target).hasClass("gem")) ? event.target : null;
			}
		}
	})
})

function windowsSet() {
	GEM_SIZE = (window.innerWidth < (96 * NUM_COLS)) ? (window.innerWidth - 10) / NUM_COLS : 96;
	$("#game-field").css({
		"background-color": "#000000",
		"width": (NUM_COLS * GEM_SIZE) + "px",
		"height": (NUM_ROWS * GEM_SIZE) + "px",
		"position": "relative"
	});
	$("#marker").css({
		"width": GEM_SIZE + "px",
		"height": GEM_SIZE + "px",
		"border": "5px solid white",
		"position": "absolute"
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
			$("#game-field").append('<div class = "' + GEM_CLASS + '" id = "' + GEM_ID_PREFIX + '_' + i + '_' + j + `">` + getImg(jewels[i][j]) + `</div>`);
			$("#" + GEM_ID_PREFIX + "_" + i + "_" + j).css({
				"top": (i * GEM_SIZE) + 4 + "px",
				"left": (j * GEM_SIZE) + 4 + "px",
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
				if (is_rainbow(selectedRow, selectedCol) || is_rainbow(posY, posX)) {
					gameState = "remove";
					if (is_rainbow(selectedRow, selectedCol)) {
						removeColor(posY, posX, selectedRow, selectedCol)
					}
					if (is_rainbow(posY, posX)) {
						removeColor(selectedRow, selectedCol, posY, posX)
					}
					gemFade();
					account.moves--;
					multiplyScore = 1;
				} else if (!isStreak(selectedRow, selectedCol) && !isStreak(posY, posX)) {
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

function is_rainbow(row, col) {
	const gem = document.getElementById(GEM_ID_PREFIX + "_" + row + "_" + col);
	if (gem !== null) {
		return (gem.classList.contains('rainbow'))
	} else return false
}

function removeColor(row, col, rainbow_row, rainbow_col) {
	const gemClass = document.getElementById(GEM_ID_PREFIX + "_" + row + "_" + col).classList[1];
	const gemValue = jewels[row][col];
	for (let i = 0; i < NUM_ROWS; i++) {
		for (let j = 0; j < NUM_COLS; j++) {
			if (jewels[i][j] === gemValue) {
				document.getElementById(GEM_ID_PREFIX + "_" + i + "_" + j).classList.add(gemClass);
				flash_explode(i, j);

				jewels[i][j] = -1;
			}
		}
	}
	flash_explode(rainbow_row, rainbow_col)
	jewels[rainbow_row][rainbow_col] = -1
}

function placeNewGems() {
	let gemsPlaced = 0;
	for (let i = 0; i < NUM_COLS; i++) {
		if (jewels[0][i] === -1) {
			jewels[0][i] = Math.floor(Math.random() * difficultly);
			$("#game-field").append('<div class = "' + GEM_CLASS + '" id = "' + GEM_ID_PREFIX + '_0_' + i + `">` + getImg(jewels[0][i]) + `</div>`);
			$("#" + GEM_ID_PREFIX + "_0_" + i).css({
				"top": 4 + "px",
				"left": (i * GEM_SIZE) + 4 + "px",
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
	const v_streak = verticalStreak(row, col)
	const h_streak = horizontalStreak(row, col)
	const gem = $("#" + GEM_ID_PREFIX + "_" + row + "_" + col)
	let flash_str = flash_explode(row, col, false);
	if (gemValue !== -1) {
		if (v_streak > 3 || h_streak > 3) {
			gem.addClass("rainbow");
		} else if (v_streak > 1 && h_streak > 1) {
			gem.addClass("double-flash");
		} else if (h_streak > 2) {
			gem.addClass("horizontal-flash");
		} else if (v_streak > 2) {
			gem.addClass("vertical-flash");
		} else {
			flash_explode(row, col);
		}
		let tmp = row;
		if (v_streak > 1) {
			while (flash_str === "double-flash" || flash_str === "horizontal-flash" || tmp > 0 && jewels[tmp - 1][col] === gemValue) {
				flash_str = flash_explode(tmp - 1, col);
				tmp--;
			}
			tmp = row;
			while (flash_str === "double-flash" || flash_str === "horizontal-flash" || tmp < NUM_ROWS - 1 && jewels[tmp + 1][col] === gemValue) {
				flash_str = flash_explode(tmp + 1, col);
				tmp++;
			}
		}
		if (h_streak > 1) {
			tmp = col;
			while (flash_str === "double-flash" || flash_str === "vertical-flash" || tmp > 0 && jewels[row][tmp - 1] === gemValue) {
				flash_str = flash_explode(row, tmp - 1);
				tmp--;
			}
			tmp = col;
			while (flash_str === "double-flash" || flash_str === "vertical-flash" || tmp < NUM_COLS - 1 && jewels[row][tmp + 1] === gemValue) {
				flash_str = flash_explode(row, tmp + 1);
				tmp++;
			}
		}
		account.score += multiplyScore;
	}
}


function flash_explode(row, col, del_self = true) {
	let flash_str = ''
	const gem = document.getElementById(GEM_ID_PREFIX + "_" + row + "_" + col);
	if (gem !== null && jewels[row][col] !== -1) {
		if (gem.classList.contains('rainbow')) {
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
			gem.classList.add("remove");
			jewels[row][col] = -1
		} else if (gem.classList.contains('double-flash')) {
			removeGem(row, col)
			removeRow(row);
			removeCol(col);
			flash_str = 'double-flash'
		} else if (gem.classList.contains('horizontal-flash')) {
			removeGem(row, col)
			removeRow(row);
			flash_str = 'horizontal-flash'
		} else if (gem.classList.contains('vertical-flash')) {
			removeGem(row, col)
			removeCol(col);
			flash_str = 'vertical-flash'
		} else if (del_self) {
			removeGem(row, col)
		}
	}
	return flash_str
}

function removeGem(row, col) {
	$("#" + GEM_ID_PREFIX + "_" + row + "_" + col).addClass("remove");
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
	return streak
}

function horizontalStreak(row, col) {
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
	return streak
}

function isStreak(row, col) {
	return verticalStreak(row, col) > 1 || horizontalStreak(row, col) > 1;
}
