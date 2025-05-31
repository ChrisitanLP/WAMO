/**
 * Class responsible for handling all contact-related operations
 */
class ContactManager {
    constructor() {
        this.csrfToken = $('meta[name="csrf-token"]').attr('content');
        this.initEventListeners();
    }

    /**
     * Initialize event listeners for contact operations
     */
    initEventListeners() {
        $(document).on('click', '.save-contact-btn', (e) => this.handleSaveContact(e));
        $(document).on('click', '.contact-plus-icon', (e) => this.handleAddContact(e));
        $(document).on('click', '.profile-pic', (e) => this.handleContactSelect(e));
    }

    /**
     * Handle saving a contact to the system
     * @param {Event} e - The click event
     */
    handleSaveContact(e) {
        e.stopPropagation();
        
        const $button = $(e.currentTarget);
        const contactData = {
            clientId: $button.data('client-id'),
            contactNumber: $button.data('contact-phone'),
            contactName: $button.data('contact-name')
        };
        
        this.saveContact(contactData);
    }

    /**
     * Save contact to the backend
     * @param {Object} contactData - Contact information
     */
    saveContact(contactData) {
        $.ajax({
            url: '/api/contacts/save',
            type: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(contactData),
            success: (data) => this.handleSaveContactResponse(data),
            error: (xhr) => this.handleApiError(xhr, 'añadir el contacto')
        });
    }

    /**
     * Handle the response from saving a contact
     * @param {Object} data - Response data from the API
     */
    handleSaveContactResponse(data) {
        if (!data.result) return;

        switch (data.result.status) {
            case 'success':
                NotificationService.showSuccess('Guardado!', 'El contacto ha sido guardado correctamente.')
                    .then(() => {
                        if (window.modal_contact?.hasClass('show')) {
                            window.modal_contact.modal('hide');
                        }
                    });
                break;
            case 'exists':
                NotificationService.showInfo('Contacto Existente', 'El contacto ya está guardado en el sistema.');
                break;
            default:
                NotificationService.showError('Error!', data.message || 'No se pudo guardar el contacto.');
        }
    }

    /**
     * Handle adding a contact
     * @param {Event} e - The click event
     */
    handleAddContact(e) {
        e.stopPropagation();
        
        const $item = $(e.currentTarget).closest('.contact-item');
        const contactData = {
            name: $item.find('.contact-name').text(),
            phone_number: $item.find('.contact-phone').text(),
            profile_pic_url: $item.find('.profile-pic img').attr('src')
        };
        
        this.addContact(contactData);
    }

    /**
     * Add a contact to the system
     * @param {Object} contactData - Contact information
     */
    addContact(contactData) {
        $.ajax({
            url: '/api/contact/add',
            type: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(contactData),
            success: (data) => this.handleAddContactResponse(data),
            error: (xhr, status, error) => {
                NotificationService.showError('Error!', `Error en la solicitud: ${error}`);
            }
        });
    }

    /**
     * Handle the response from adding a contact
     * @param {Object} data - Response data from the API
     */
    handleAddContactResponse(data) {
        if (!data.result) return;

        if (data.result.status === 'success') {
            NotificationService.showSuccess('Éxito!', 'Contacto agregado exitosamente.');
        } else {
            NotificationService.showWarning('Advertencia!', 
                data.result.message || 'No se pudo agregar el contacto.');
        }
    }

    /**
     * Handle selecting a contact to view chat
     * @param {Event} e - The click event
     */
    handleContactSelect(e) {
        const $profilePic = $(e.currentTarget);
        const contactData = {
            serialized: $profilePic.data('serialized'),
            user_id: $profilePic.data('user-id'),
            phone_number: $profilePic.data('phone-number')
        };
        
        this.getChatByContact(contactData);
    }

    /**
     * Get chat by contact information
     * @param {Object} contactData - Contact information
     */
    getChatByContact(contactData) {
        $.ajax({
            url: '/api/chat/id',
            type: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(contactData),
            success: (data) => this.handleGetChatResponse(data),
            error: (xhr, status, error) => {
                console.error('Error en la solicitud:', error);
            }
        });
    }

    /**
     * Handle the response from getting a chat
     * @param {Object} data - Response data from the API
     */
    handleGetChatResponse(data) {
        if (!data.result || data.result.status !== 'success') return;
        
        const chatId = data.result.chat_id;
        window.chatManager.setSelectedChatId(chatId);
        
        window.chat_id_contact_section = chatId;
        window.contact_id_section = data.result.contact_id;
        
        $('#messages-container').show();
        window.chatManager.loadMessages(chatId);
    }

    /**
     * Handle API errors
     * @param {Object} xhr - XHR object
     * @param {string} context - Context of the error for user display
     */
    handleApiError(xhr, context) {
        let errorMessage = 'Error desconocido';
        
        if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMessage = xhr.responseJSON.message;
        }
        
        NotificationService.showError('Error', `Hubo un problema al ${context}: ${errorMessage}`);
    }
}