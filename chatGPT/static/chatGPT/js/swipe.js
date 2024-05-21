// Определяем начальные координаты касания
let startX = 0;
let startY = 0;

// Функция для обработки свайпов
function handleSwipe(event) {
    const touch = event.changedTouches[0];
    const deltaX = touch.pageX - startX;
    const deltaY = touch.pageY - startY;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

    // Определяем направление свайпа
    const angle = Math.atan2(deltaY, deltaX);
    const direction = angle * (180 / Math.PI);

    // Определяем пороговое значение для распознавания свайпа
    const swipeThreshold = 50; // Пороговое значение в пикселях
    const leftEdgeThreshold = window.innerWidth * 0.3; // Пороговое значение для открывания сайдбара (30% ширины экрана)

    // Обрабатываем свайпы
    if (distance > swipeThreshold && Math.abs()) {
        if (direction > -30 && direction < 30 && startX < leftEdgeThreshold) {
            // Свайп слева направо с левого края экрана
            sidebar.classList.add("shown");
            sidebar_button.classList.add("rotated");
        } else if (direction > 150 || direction < -150) {
            // Свайп справа налево
            hide_sidebar();
        }
    }
}


// Обработчики событий для свайпов
document.addEventListener("touchstart", function (event) {
    const touch = event.touches[0];
    startX = touch.pageX;
    startY = touch.pageY;
});

document.addEventListener("touchend", function (event) {
    handleSwipe(event);
});
