function localeDate(dateString) {
    const date = new Date(dateString);

    const day = date.getDate().toString().padStart(2, '0');
    const monthIndex = date.getMonth();
    const year = date.getFullYear().toString();

    const months = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ];

    const month = months[monthIndex];

    return `${day} ${month} ${year} г.`;
}
