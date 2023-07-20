function showEl(el) {
    el.classList.remove('visually-hidden');
}

function hideEl(el) {
    el.classList.add('visually-hidden');
}

function toggleEl(el) {
    if (el.classList.contains('visually-hidden')) {
        hideEl(el);
    } else showEl(el);
}

function hideElByID(id) {
    const el = document.getElementById(id)
    hideEl(el);
}

function toggleElByID(id) {
    const el = document.getElementById(id)
    toggleEl(el);
}

function showElByID(id) {
    const el = document.getElementById(id)
    showEl(el);
}

function showElements(...elements) {
    for (let el in elements) {
        showEl(document.querySelector(el))
    }
}

function hideElements(...elements) {
    for (let el in elements) {
        hideEl(document.querySelector(el))
    }
}
