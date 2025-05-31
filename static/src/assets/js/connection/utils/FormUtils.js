// utils/FormUtils.js
class FormUtils {
    constructor() {
        this.alertService = new AlertService();
    }

    validateForm() {
        const name = $('#connection_name').val().trim();
        const phoneNumber = $('#connection_phone_number').val().trim();
        const color = $('#connection_color').val();
        const countryCode = $('#country_code').val();
        
        if (!name || !phoneNumber || !color || !countryCode) {
            this.alertService.showWarningAlert('Todos los campos son requeridos.');
            return false;
        }
        return true;
    }

    prepareConnectionFormData() {
        const name = $('#connection_name').val();
        const phoneNumber = $('#connection_phone_number').val();
        const color = $('#connection_color').val();
        const countryCode = $('#country_code').val();
        const fullNumber = countryCode + phoneNumber;

        const formData = new FormData();
        formData.append('name', name);
        formData.append('phone_number', fullNumber);
        formData.append('color', color);

        return formData;
    }

    resetConnectionForm() {
        $('#connection_name').val('');
        $('#connection_phone_number').val('');
        $('#connection_color').val('');
        $('#country_code').val('');
    }

    extractErrorMessage(xhr) {
        if (xhr.responseJSON && xhr.responseJSON.message) {
            return xhr.responseJSON.message;
        }
        return xhr.responseText || 'Error desconocido.';
    }
}