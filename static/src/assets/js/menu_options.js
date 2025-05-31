$(document).ready(function () {
    document.querySelector('header').remove();
    document.querySelector('footer').remove();

     // Esperar a que SweetAlert2 esté definido
    if (typeof Swal === "undefined") {
        console.error("SweetAlert2 no está cargado correctamente.");
        return;
    }

    if (document.body.getAttribute('data-show-admin-error') === 'True') {
        showAdminRequiredAlert();
    }
    
    // Función para mostrar alerta de error de permisos de administrador
    function showAdminRequiredAlert() {
        Swal.fire({
            icon: 'error',
            title: 'Acceso Restringido',
            text: 'Solo los administradores pueden acceder a la sección de conexiones.',
            timer: 6000,
            timerProgressBar: true
        });
    }
});