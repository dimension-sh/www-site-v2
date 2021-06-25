// Amazingly simple theme switcher
//
// 1. Define a CSS document as a link with a id of 'theme'
// 2. Call change_theme(name) from wherever

document.addEventListener('DOMContentLoaded', function(){ 
    var prev_theme = localStorage.getItem("theme");
    if (prev_theme != null) {
        change_theme(prev_theme);
    }
}, false);

function change_theme(name) {
    document.getElementById('theme').href = '/css/' + name + '.css';
    localStorage.setItem("theme", name);
}