class MessageEditManager {
    constructor() {
        this.csrfToken = $('meta[name="csrf-token"]').attr('content');
        this.init();
    }
  
    init() {
        this.bindEvents();
    }
  
    bindEvents() {
        $(document).on('click', '.edit-message', this.handleEditButtonClick);
        $('#confirm-edit-btn').on('click', this.handleConfirmEdit);
        $('#lightbox-close').on('click', this.closeEditModal);
        $(document).on('click', this.handleOutsideModalClick);
        $(document).on('click', '.important-message', (e) => this.handleToggleImportant(e));
        $(document).on('click', '.reply-message', (e) => this.handleReplyToMessage(e));
        $(document).on('click', '#cancel-reply-btn', () => this.handleCancelReply());
        $(document).on('click', '.delete-message', (e) => this.handleDeleteMessage(e));
    }

    /* ************************************************************ Edit Message ************************************************************  */
  
    handleEditButtonClick(e) {
        e.stopPropagation();
    
        const messageId = $(e.currentTarget).data('message-id');
        const messageElement = $(e.currentTarget).closest('.message');
        const messageContent = messageElement.find('.text-message-body').text();
    
        $('#editMessageModal .message-bubble').text(messageContent);
        $('#edit-message-input')
            .val(messageContent)
            .data('editing-message-id', messageId);
        
        $('#editMessageModal').fadeIn();
    }
  
    handleConfirmEdit() {
        const messageId = $('#edit-message-input').data('editing-message-id');
        const newContent = $('#edit-message-input').val();
        const chatId = window.selectedChat;
    
        if (!messageId) return;
    
        NotificationService.showConfirmation(
            '¿Editar mensaje?',
            '¿Estás seguro de que quieres editar este mensaje?',
            'Sí, editar'
        ).then((result) => {
            if (result.isConfirmed) {
                MessageService.editMessage(messageId, newContent)
                    .done(response => {
                        if (response.status === 'success') {
                            $(`.message[data-message-id="${messageId}"]`)
                                .find('.message-text')
                                .text(newContent);
    
                            $('#editMessageModal').fadeOut();
                            MessageService.loadMessages(chatId);
                            NotificationService.showSuccess('Mensaje editado', 'El mensaje se ha editado correctamente.');
                        } else {
                            NotificationService.showWarning('Advertencia', 'El mensaje ya no se puede editar.');
                        }
                    })
                    .fail(() => {
                        $('#editMessageModal').fadeOut();
                        NotificationService.showError('Error', 'Error en la solicitud de edición.');
                    });
            }
        });
    }
  
    closeEditModal() {
        $('#editMessageModal').fadeOut();
    }
  
    handleOutsideModalClick(e) {
        const modal = $('#editMessageModal .modal-content');
        if (!modal.is(e.target) && modal.has(e.target).length === 0) {
            $('#editMessageModal').fadeOut();
        }
    }

    /* ************************************************************ Message as Important ************************************************************  */

    /**
     * Handle toggling a message as important
     * @param {Event} e - The click event
     */
    handleToggleImportant(e) {
        e.stopPropagation();
        
        if (!window.chatManager.getSelectedChatId()) return;
        
        const $button = $(e.currentTarget);
        const messageId = $button.data('message-id');
        const isStarred = $button.data('is-starred');
        
        this.handleConfirmToggleImportant(messageId, isStarred);
    }

    /**
     * Show confirmation dialog for toggling important status
     * @param {string} messageId - ID of the message
     * @param {boolean} isStarred - Whether the message is currently starred
     */
    handleConfirmToggleImportant(messageId, isStarred) {
        const title = isStarred ? '¿Quitar destaque?' : '¿Destacar?';
        const text = isStarred 
            ? 'Este mensaje se desmarcará como importante.' 
            : 'Este mensaje se marcará como importante.';
        const confirmText = isStarred ? 'Sí, quitar destaque' : 'Sí, destacar';
        
        NotificationService.showConfirmation(title, text, confirmText)
            .then((result) => {
                if (result.isConfirmed) {
                    this.toggleMessageImportance(messageId, isStarred);
                }
            });

        $('.message-options-menu').remove();
    }

    /**
     * Toggle a message's importance status
     * @param {string} messageId - ID of the message
     * @param {boolean} isStarred - Whether the message is currently starred
     */
    toggleMessageImportance(messageId, isStarred) {
        const apiUrl = isStarred 
            ? '/api/message/unmark_important' 
            : '/api/message/mark_important';
        
        $.ajax({
            url: apiUrl,
            type: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({ message_id: messageId }),
            success: (response) => this.handleToggleImportantResponse(response, isStarred),
            error: () => {
                NotificationService.showError('Error', 'No se pudo cambiar el estado de destaque del mensaje.');
            }
        });
    }

    /**
     * Handle the response from toggling message importance
     * @param {Object} response - Response data from the API
     * @param {boolean} isStarred - Whether the message was starred
     */
    handleToggleImportantResponse(response, isStarred) {
        if (response.status === 'success') {
            window.chatManager.loadMessages(window.chatManager.getSelectedChatId());
            
            const title = isStarred ? 'Quitar destaque' : '¡Destacado!';
            NotificationService.showSuccess(title, response.message);
        } else {
            NotificationService.showError('¡Error!', 'No se pudo cambiar el estado de destaque del mensaje.');
        }
    }

    /* ************************************************************ Reply Message ************************************************************  */

    /**
     * Handle replying to a message
     * @param {Event} e - The click event
     */
    handleReplyToMessage(e) {
        e.stopPropagation();
        
        if (!window.chatManager.getSelectedChatId()) return;
        
        const $button = $(e.currentTarget);
        const messageId = $button.data('message-id');
        window.chatManager.setSelectedMessageId(messageId);
        
        const indexMessage = $button.data('message-index');
        this.setupReplyInterface(indexMessage, messageId);
    }

    /**
     * Set up the reply interface for a specific message
     * @param {string} indexMessage - Index of the message
     * @param {string} messageId - ID of the message
     */
    setupReplyInterface(indexMessage, messageId) {
        const $messageElement = $('#' + indexMessage);
        
        if (!$messageElement.length) {
            console.error('No se encontró el mensaje con el índice especificado:', indexMessage);
            return;
        }
        
        const messageText = $messageElement.find('.text-message-body').html();
        const fromName = $messageElement.hasClass('from-me') 
            ? 'Tú' 
            : $('.chat-banner .chat-name').text();
        const messageType = $messageElement.data('message-type');
        
        $('#reply-name').text(fromName);
        
        // Set appropriate icon based on message type
        this.setReplyContentByType(messageType, messageText);
        
        window.showReplyContainer();
        $('#reply-container').data('reply-message-id', messageId);
    }

    /**
     * Set reply content based on message type
     * @param {string} messageType - Type of the message
     * @param {string} messageText - Text content of the message
     */
    setReplyContentByType(messageType, messageText) {
        let iconHtml = '';
        
        switch (messageType) {
            case 'image':
                iconHtml = '<span><i class="fa fa-image" aria-hidden="true"></i> Imagen</span>';
                break;
            case 'video':
                iconHtml = '<span><i class="fa fa-video-camera" aria-hidden="true"></i> Video</span>';
                break;
            case 'document':
                iconHtml = '<span><i class="fa fa-file" aria-hidden="true"></i> Documento</span>';
                break;
            case 'audio':
            case 'ptt':
                iconHtml = '<span><i class="fa fa-microphone" aria-hidden="true"></i> Audio</span>';
                break;
            case 'groups_v4_invite':
                iconHtml = '<span><i class="fa fa-users" aria-hidden="true"></i> Invitación de Grupo</span>';
                break;
            case 'sticker':
                iconHtml = '<span><i class="fa fa-sticky-note" aria-hidden="true"></i> Sticker</span>';
                break;
            default:
                $('#reply-text').html(messageText);
                return;
        }
        
        $('#reply-text').html(iconHtml);
    }

    /**
     * Handle canceling reply to a message
     */
    handleCancelReply() {
        window.chatManager.setSelectedMessageId(null);
        window.hideReplyContainer();
        $('#reply-text').text('');
        $('#reply-name').text('');
        $('#reply-container').removeData('reply-message-id');
    }

    /* ************************************************************ Delete Message ************************************************************  */

    /**
     * Handle deleting a message
     * @param {Event} e - The click event
     */
    handleDeleteMessage(e) {
        e.stopPropagation();
        
        if (!window.chatManager.getSelectedChatId()) return;
        
        const messageId = $(e.currentTarget).data('message-id');
        this.handleConfirmDelete(messageId);
    }

    /**
     * Show confirmation dialog for deleting a message
     * @param {string} messageId - ID of the message
     */
    handleConfirmDelete(messageId) {
        NotificationService.showConfirmation(
            '¿Estás seguro?',
            'Este mensaje será eliminado y no podrás deshacer esta acción.',
            'Sí, eliminar'
        ).then((result) => {
            if (result.isConfirmed) {
                this.deleteMessage(messageId);
            }
        });
        
        $('.message-options-menu').remove();
    }

    /**
     * Delete a message
     * @param {string} messageId - ID of the message
     */
    deleteMessage(messageId) {
        $.ajax({
            url: '/api/message/delete',
            type: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({ message_id: messageId }),
            success: (data) => this.handleDeleteMessageResponse(data),
            error: () => {
                NotificationService.showError('Error!', 'No se pudo eliminar el mensaje.');
            }
        });
    }

    /**
     * Handle the response from deleting a message
     * @param {Object} data - Response data from the API
     */
    handleDeleteMessageResponse(data) {
        if (data.status === 'success') {
            window.chatManager.loadMessages(window.chatManager.getSelectedChatId());
            NotificationService.showSuccess('Eliminado!', 'El mensaje ha sido eliminado.');
        } else {
            console.error('Error al eliminar el mensaje:', data.message);
            NotificationService.showError('Error!', 'No se pudo eliminar el mensaje.');
        }
    }
}