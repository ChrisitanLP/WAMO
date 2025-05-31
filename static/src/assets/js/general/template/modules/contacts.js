class ContactsModule {
    constructor() {
        this.initialize();
    }

    initialize() {
        this.initializeSearch();
        this.initializeContactModal();
    }

    initializeSearch() {
        const searchInput = $('#search-input');
        searchInput.on('input', this.debounce(this.performSearch, 300));
    }

    performSearch() {
        const query = $('#search-input').val();
        
        $.ajax({
            url: '/api/contacts/search',
            method: 'POST',
            data: { query },
            dataType: 'json',
            success: this.handleSearchSuccess,
            error: function(error) {
                console.error('Error en búsqueda de contactos:', error);
            }
        });
    }

    handleSearchSuccess(result) {
        if (result.status !== 'success') {
            console.error('Error:', result.message);
            return;
        }
        
        const contacts = result.contacts.sort((a, b) => a.name.localeCompare(b.name));
        this.renderContacts(contacts);
    }

    renderContacts(contacts) {
        const contactsGrid = $('.contacts-grid');
        contactsGrid.empty();
        
        contacts.forEach(contact => {
            const contactItem = this.createContactItemHTML(contact);
            contactsGrid.append(contactItem);
        });
    }

    createContactItemHTML(contact) {
        return `
            <div class="contact-item" data-contact-id="${contact.id}" data-user-id="${contact.user_id}" data-phone-number="${contact.phone_number}" data-color-contact="${contact.color}">
                <div class="color-line" style="background-color: ${contact.color}"></div>
                <div class="profile-pic" data-contact-id="${contact.id}" data-serialized="${contact.serialized}" data-user-id="${contact.user_id}" data-phone-number="${contact.phone_number}">
                    <img src="${contact.profile_pic_url || 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg'}" alt="Profile Picture"/>
                </div>
                <div class="contact-info">
                    <div class="contact-name">${contact.name}</div>
                    <div class="contact-phone">${contact.phone_number}</div>
                    <div class="contact-user">${contact.user_display_name}</div>
                </div>
                <div class="contact-plus-icon">
                    <i class="fa fa-plus"></i>
                </div>
            </div>`;
    }

    initializeContactModal() {
        $('#add-contact-btn').on('click', () => {
            $('#add-contact-modal').modal('show');
            this.loadWhatsappUsers();
        });
        
        $('#header-close-modal-contact, #footer-close-modal-contact').on('click', function() {
            $('#add-contact-modal').modal('hide');
        });
        
        $('#save-contact-btn').on('click', () => this.saveContact());
    }

    loadWhatsappUsers() {
        $.ajax({
            url: '/api/whatsapp_users',
            method: 'GET',
            dataType: 'json',
            success: function(result) {
                if (result.status !== 'success') {
                    console.error('Error al obtener usuarios:', result.message);
                    return;
                }
                
                const userSelect = $('#contact_user');
                userSelect.empty();
                userSelect.append('<option value="">Seleccionar Usuario</option>');
                
                result.users.forEach(user => {
                    userSelect.append(`<option value="${user.id}">${user.name}</option>`);
                });
            },
            error: function(error) {
                console.error('Error en la solicitud AJAX:', error);
            }
        });
    }

    saveContact() {
        if (!this.validateContactForm()) {
            return;
        }
        
        const contactData = {
            clientId: $('#contact_user').val(),
            contactNumber: $('#contact-country_code').val() + $('#contact_phone_number').val(),
            contactName: $('#contact_name').val()
        };
        
        $.ajax({
            url: '/api/contacts/save',
            type: 'POST',
            headers: {
                'X-CSRFToken': $('meta[name="csrf-token"]').attr('content'),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(contactData),
            success: this.handleSaveContactSuccess,
            error: this.handleSaveContactError
        });
    }

    handleSaveContactSuccess(data) {
        if (!data.result) {
            showAlert('error', 'Error!', 'Respuesta de servidor inválida.');
            return;
        }
        
        if (data.result.status === 'success') {
            showAlert('success', 'Éxito', 'Contacto añadido exitosamente.')
                .then(() => $('#add-contact-modal').modal('hide'));
        } else {
            showAlert('error', 'Error!', data.message || 'No se pudo guardar el contacto.');
        }
    }

    handleSaveContactError(xhr) {
        const errorMessage = xhr.responseJSON?.message || 'Error desconocido.';
        showAlert('error', 'Error', 'Hubo un problema al añadir el contacto: ' + errorMessage);
    }

    validateContactForm() {
        const name = $('#contact_name').val().trim();
        const phoneNumber = $('#contact_phone_number').val().trim();
        const countryCode = $('#contact-country_code').val();
        const userId = $('#contact_user').val();
        
        if (!name || !phoneNumber || !countryCode || !userId) {
            showAlert('warning', 'Advertencia!', 'Todos los campos son requeridos.');
            return false;
        }
        
        if (phoneNumber.length !== 9) {
            $('#phone-error').show();
            return false;
        }
        
        $('#phone-error').hide();
        return true;
    }

    debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
}