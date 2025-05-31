// ui/AlertService.js
class AlertService {
    showWarningAlert(message) {
        return Swal.fire({
            icon: 'warning', 
            title: 'Advertencia!',
            text: message,
            confirmButtonText: 'Aceptar'
        });
    }

    showSuccessAlert(response) {
        return Swal.fire({
            title: 'Éxito',
            text: response.message || 'Conexión creada exitosamente.',
            icon: 'success',
            confirmButtonText: 'Aceptar'
        });
    }

    showErrorAlert(message) {
        return Swal.fire({
            title: 'Error',
            text: 'Hubo un problema al crear la conexión: ' + message,
            icon: 'error',
            confirmButtonText: 'Aceptar'
        }).then(() => {
            const connectionModal = $('#connection-modal');
            connectionModal.modal('hide')
        });
    }

    showConfirmDeleteAlert() {
        return Swal.fire({
            title: '¿Estás seguro?',
            text: "No podrás revertir esto!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, eliminarla!',
            cancelButtonText: 'Cancelar'
        });
    }

    showDeleteSuccessAlert() {
        return Swal.fire({
            title: '¡Eliminado!',
            text: 'La conexión ha sido eliminada.',
            icon: 'success',
            confirmButtonText: 'Aceptar'
        });
    }

    showDeleteErrorAlert(errorMessage) {
        return Swal.fire({
            title: 'Error',
            text: 'Hubo un problema al eliminar la conexión: ' + errorMessage,
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
    }

    showAuthenticatedAlert(number) {
        return Swal.fire({
            icon: 'success',
            title: '¡Autenticación Exitosa!',
            text: `El número ${number} ha sido autenticado correctamente.`,
            timer: 6000,
            timerProgressBar: true
        });
    }

    showReadyAlert(number) {
        return Swal.fire({
            icon: 'info',
            title: 'WhatsApp Listo',
            text: `El cliente de WhatsApp para ${number} está listo para usar.`,
            timer: 6000,
            timerProgressBar: true
        });
    }

    showAlreadyAuthenticatedAlert(phoneNumber) {
        return Swal.fire({
            icon: 'success',
            title: 'Ya Autenticado',
            text: `El número ${phoneNumber} ya está autenticado y listo para usar.`,
            timer: 3000,
            timerProgressBar: true
        });
    }
}