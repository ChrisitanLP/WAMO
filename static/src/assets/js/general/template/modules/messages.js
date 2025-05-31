class MessagesModule {
    constructor() {
        this.initialize();
    }

    initialize() {
        this.initializeMessageModal();
        this.initializeMessageDeletion();
    }

    initializeMessageModal() {
        this.addMessageBtn = $('#add-message-btn');
        this.modal = $('#add-message-modal');
        this.closeButtons = $('#header-close-modal, #footer-close-modal');
        this.saveMessageBtn = $('#save-message-btn');
        this.messageTypeSelect = $('#message-type');

        this.addMessageBtn.on('click', () => this.modal.modal('show'));
        this.closeButtons.on('click', () => this.modal.modal('hide'));
        this.messageTypeSelect.on('change', () => this.updateFormFields());
        this.saveMessageBtn.on('click', () => this.saveMessage());

        this.updateFormFields();
    }

    updateFormFields() {
        const selectedType = $('#message-type').val();
        const messageContentGroup = $('#message-content-group');
        const pdfFileGroup = $('#pdf-file-group');
        const locationGroup = $('#location-group');
        const messageContentTextarea = $('#message-content');

        messageContentGroup.hide();
        pdfFileGroup.hide();
        locationGroup.hide();
        messageContentTextarea.prop('disabled', true);

        switch (selectedType) {
            case 'text':
            case 'web_page':
                messageContentGroup.show();
                messageContentTextarea.prop('disabled', false);
                break;
            case 'image':
            case 'document':
                pdfFileGroup.show();
                break;
            case 'location':
                locationGroup.show();
                break;
        }
    }

    saveMessage() {
        const messageData = this.collectMessageFormData();

        $.ajax({
            url: '/api/default_message/create',
            method: 'POST',
            data: messageData,
            processData: false,
            contentType: false,
            success: (response) => this.handleSaveMessageSuccess(response),
            error: (xhr) => this.handleSaveMessageError(xhr)
        });
    }

    collectMessageFormData() {
        const formData = new FormData();
        const type = $('#message-type').val();

        formData.append('name', $('#message-name').val());
        formData.append('type', type);

        switch (type) {
            case 'text':
            case 'web_page':
                formData.append('text', $('#message-content').val());
                formData.append('web_url', type === 'web_page' ? $('#message-content').val() : '');
                break;
            case 'location':
                formData.append('location', $('#latitude').val() + ',' + $('#longitude').val());
                formData.append('location_latitude', $('#latitude').val());
                formData.append('location_longitude', $('#longitude').val());
                break;
            case 'document':
            case 'image':
                const file = $('#pdf-file').prop('files')[0];
                if (file) {
                    formData.append('file', file);
                    formData.append('file_name', file.name);
                }
                break;
        }

        return formData;
    }

    handleSaveMessageSuccess(response) {
        if (!response.success) {
            showAlert('error', 'Error', 'Hubo un problema al crear el mensaje: ' + response.message);
            return;
        }

        showAlert('success', 'Éxito', 'Mensaje creado exitosamente.')
            .then((result) => {
                if (result.isConfirmed) {
                    $('#add-message-modal').modal('hide');
                    this.renderMessages(response.messages);
                }
            });
    }

    handleSaveMessageError(xhr) {
        let errorMessage = 'Error desconocido.';
        if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMessage = xhr.responseJSON.message;
        } else if (xhr.responseText) {
            errorMessage = xhr.responseText;
        }

        showAlert('error', 'Error', 'Hubo un problema al crear el mensaje: ' + errorMessage);
    }

    renderMessages(messages) {
        const messagesGrid = $('.messages-grid');
        messagesGrid.empty();

        messages.forEach(message => {
            const messageItem = this.createMessageItemHTML(message);
            messagesGrid.append(messageItem);
        });
    }

    createMessageItemHTML(message) {
        let messageContent = '';

        switch (message.type) {
            case 'text':
                messageContent = message.text;
                break;
            case 'location':
                messageContent = `<a href="https://www.google.com/maps?q=${message.location_latitude},${message.location_longitude}" target="_blank">Ver ubicación</a>`;
                break;
            case 'image':
                messageContent = `<pre>${message.file_name}</pre>`;
                break;
            case 'document':
                messageContent = message.file_name;
                break;
            case 'web_page':
                messageContent = `<a href="${message.web_url}" target="_blank">Ver página</a>`;
                break;
        }

        return $(
            `<div class="message-item" data-message-id="${message.id}">
                <div class="color-line" style="background-color: #e0ca04"></div>
                <div class="send-icon" data-message-id="${message.id}">
                    <i class="fa fa-paper-plane"></i>
                </div>
                <div class="message-info">
                    <div class="message-name">${message.name}</div>
                    <div class="message-type">${messageContent}</div>
                </div>
                <button class="close-btn">
                    <i class="fa fa-times"></i>
                </button>
            </div>`
        );
    }

    initializeMessageDeletion() {
        $('.messages-grid').on('click', '.close-btn', (event) => {
            const messageId = $(event.currentTarget).closest('.message-item').data('message-id');

            showConfirmation('¿Estás seguro?', '¡No podrás revertir esto!')
                .then((result) => {
                    if (result.isConfirmed) {
                        this.deleteMessage(messageId);
                    }
                });
        });
    }

    deleteMessage(messageId) {
        $.ajax({
            url: `/api/default_message/delete/${messageId}`,
            method: 'DELETE',
            dataType: 'json',
            success: (response) => {
                if (response.success === 'success') {
                    $(`div.message-item[data-message-id="${messageId}"]`).remove();
                    showAlert('success', '¡Eliminado!', 'El mensaje ha sido eliminado.');
                } else {
                    showAlert('error', 'Error', 'Error al eliminar el mensaje: ' + response.message);
                }
            },
            error: () => {
                showAlert('error', 'Error', 'Error al conectar con el servidor.');
            }
        });
    }
}