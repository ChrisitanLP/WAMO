// Función para mostrar alertas con SweetAlert
function showAlert(icon, title, text) {
    return Swal.fire({
        icon: icon,
        title: title,
        text: text,
        confirmButtonText: 'Aceptar'
    });
}

// Función para mostrar confirmaciones con SweetAlert
function showConfirmation(title, text) {
    return Swal.fire({
        title: title,
        text: text,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminarlo'
    });
}

// Función para evitar múltiples llamadas de búsqueda durante escritura rápida
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}