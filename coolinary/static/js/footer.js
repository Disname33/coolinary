document.addEventListener("DOMContentLoaded", function () {
    const footer = document.querySelector("footer");

    function stickFooterToBottom() {
        const windowHeight = window.innerHeight;
        const footerHeight = footer.offsetHeight;
        const footerTop = footer.getBoundingClientRect().top;

        if (footerTop + footerHeight < windowHeight) {
            const spaceBelowFooter = windowHeight - (footerTop + footerHeight);
            footer.style.marginTop = spaceBelowFooter + "px";
        } else {
            footer.style.marginTop = "0";
        }
    }

    window.addEventListener("load", stickFooterToBottom);
    window.addEventListener("resize", stickFooterToBottom);
});