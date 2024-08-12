document.addEventListener('DOMContentLoaded', function () {
    // Set the previously stored theme
    var prev_theme = localStorage.getItem("theme");
    if (prev_theme != null) {
        change_theme(prev_theme);
    }

    // Add handlers for the theme buttons
    document.querySelectorAll('a[data-theme]').forEach(el => {
        el.addEventListener('click', function () {
            change_theme(el.dataset.theme);
        });
    });
}, false);

function change_theme(name) {
    document.documentElement.setAttribute('data-theme', name)
    localStorage.setItem("theme", name);
}