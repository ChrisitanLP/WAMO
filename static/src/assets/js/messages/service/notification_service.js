class NotificationService {
    /**
     * Show a success notification
     * @param {string} title - Title of the notification
     * @param {string} message - Message to display
     * @returns {Promise} Promise from SweetAlert
     */
    static showSuccess(title, message) {
        return Swal.fire({
            title: title,
            text: message,
            icon: 'success',
            confirmButtonText: 'Aceptar'
        });
    }

    /**
     * Show an info notification
     * @param {string} title - Title of the notification
     * @param {string} message - Message to display
     * @returns {Promise} Promise from SweetAlert
     */
    static showInfo(title, message) {
        return Swal.fire({
            title: title,
            text: message,
            icon: 'info',
            confirmButtonText: 'Aceptar'
        });
    }

    /**
     * Show an error notification
     * @param {string} title - Title of the notification
     * @param {string} message - Message to display
     * @returns {Promise} Promise from SweetAlert
     */
    static showError(title, message) {
        return Swal.fire({
            title: title,
            text: message,
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
    }

    /**
     * Show a warning notification
     * @param {string} title - Title of the notification
     * @param {string} message - Message to display
     * @returns {Promise} Promise from SweetAlert
     */
    static showWarning(title, message) {
        return Swal.fire({
            title: title,
            text: message,
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
    }

    /**
     * Show a confirmation dialog
     * @param {string} title - Title of the dialog
     * @param {string} message - Message to display
     * @param {string} confirmText - Text for the confirm button
     * @returns {Promise} Promise from SweetAlert
     */
    static showConfirmation(title, message, confirmText = 'Sí') {
        return Swal.fire({
            title: title,
            text: message,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: confirmText,
            cancelButtonText: 'Cancelar'
        });
    }
}