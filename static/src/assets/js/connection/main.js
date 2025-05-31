// main.js
document.addEventListener('DOMContentLoaded', function() {
    // Remover header y footer si existen
    document.querySelector('header')?.remove();
    document.querySelector('footer')?.remove();

    new ConnectionsManager();
});