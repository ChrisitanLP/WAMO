class ChatManager {
    constructor() {
      this.selectedChatId = null;
      this.selectedMessageId = null;
      this.selectedSessionId = null;
      this.csrfToken = $('meta[name="csrf-token"]').attr('content');
      this.init();
    }

    /**
     * Initialize event listeners for chat operations
     */
    initEventListeners() {
        $(document).on('click', '.product-item', (e) => this.handleProductSelect(e));
    }

    /**
     * Set the selected chat ID
     * @param {string} chatId - ID of the selected chat
     */
    setSelectedChatId(chatId) {
        this.selectedChatId = chatId;
    }

    /**
     * Get the selected chat ID
     * @returns {string} The selected chat ID
     */
    getSelectedChatId() {
        return this.selectedChatId;
    }

    /**
     * Set the selected message ID for reply
     * @param {string} messageId - ID of the selected message
     */
    setSelectedMessageId(messageId) {
        this.selectedMessageId = messageId;
    }

    /**
     * Get the selected message ID
     * @returns {string} The selected message ID
     */
    getSelectedMessageId() {
        return this.selectedMessageId;
    }

    init() {
      this.fetchSessionId();
      this.bindEvents();
      UIManager.showAttendButton();
      this.initEventListeners();
    }
    
    bindEvents() {
        $(document).on('click', '.chat-item', this.handleChatSelection.bind(this));
        $(document).on('click', '.attend-button', this.handleAttendChat.bind(this));
        $(document).on('click', '.chat-close-icon', this.handleCloseChat.bind(this));
        $(document).on('click', '.chat-ready-icon', this.handleCompleteChat.bind(this));
        $('#send-message-btn').on('click', this.handleSendMessage.bind(this));
    }
    
    fetchSessionId() {
        
        return $.ajax({
            url: '/session_id',
            type: 'GET',
            headers: {
                'X-CSRFToken': this.csrfToken
            }
        })
        .done(data => {
            if (data && data.status === 'success') {
                this.selectedSessionId = data.session;
                window.selectSessionUserId = this.selectedSessionId;
            }
        })
        .fail((xhr, status, error) => {
            console.error('Session ID fetch error:', error);
        });
    }
    
    handleChatSelection(e) {
        e.stopPropagation();
        this.selectedChatId = $(e.currentTarget).data('chat-id');
        window.selectedChat = this.selectedChatId;
        
        // Reset UI elements
        $('#message-input').val('');
        FilePreviewManager.hidePreview();
        
        if (this.selectedChatId) {
            $('#messages-container').show();
            MessageService.loadMessages(this.selectedChatId);
        } else {
            $('#messages-container').hide();
            UIManager.showMessageInput();
        }
    }

    /**
     * Handle selecting a product to send
     * @param {Event} e - The click event
     */
    handleProductSelect(e) {
        const $product = $(e.currentTarget);
        const productId = $product.data('product-id');
        const chatId = this.selectedChatId;
        
        if (!chatId) {
            console.log('No se ha seleccionado un chat.');
            return;
        }

        // Check if the user can send messages in this chat
        if (window.currentChatStatus !== 'atendiendo' || 
            window.currentAssignedUserId !== window.selectedSessionId) {
            return;
        }

        this.sendProductMessage(chatId, productId);
    }

    /**
     * Send a product message to a chat
     * @param {string} chatId - ID of the chat
     * @param {string} productId - ID of the product
     */
    sendProductMessage(chatId, productId) {
        $.ajax({
            url: '/api/message/send-product',
            type: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                chat_id: chatId,
                product_id: productId
            }),
            success: (data) => this.handleSendProductResponse(data, chatId),
            error: (xhr, status, error) => {
                console.error('Error en la solicitud:', error);
            }
        });
    }

     /**
     * Handle the response from sending a product
     * @param {Object} data - Response data from the API
     * @param {string} chatId - ID of the chat
     */
     handleSendProductResponse(data, chatId) {
        if (data.result && data.result.status === 'success') {
            this.loadMessages(chatId);
        } else {
            console.error('Error al enviar el producto:', data.message);
        }
    }
    
    handleAttendChat() {
        if (!this.selectedChatId) {
            $('#messages-container').hide();
            UIManager.showAttendButton();
            return;
        }
    
        ChatService.updateChatStatus(this.selectedChatId, 'atendiendo')
            .done(data => {
            if (data.result && data.result.status === 'success') {
                this.moveToAttendedSection(this.selectedChatId);
                UIManager.showMessageInput();
            }
        })
        .fail((xhr, status, error) => {
            this.handleApiError('Error al actualizar el estado del chat', error);
        });
    }
    
    handleCloseChat(e) {
        const chatId = $(e.currentTarget).data('chat-id');
        
        if (!chatId) {
            $('#messages-container').hide();
            UIManager.showMessageInput();
            return;
        }
    
        UIManager.showAttendButton();
    
        ChatService.updateChatStatus(chatId, 'pendiente')
            .done(data => {
            if (data.result && data.result.status === 'success') {
                this.moveToPendingSection(chatId, data.result);
                UIManager.showAttendButton();
            }
        })
            .fail((xhr, status, error) => {
            this.handleApiError('Error al actualizar el estado del chat', error);
        });
    }
    
    handleCompleteChat(e) {
        const chatId = $(e.currentTarget).data('chat-id');
        
        if (!chatId) {
            $('#messages-container').hide();
            UIManager.showMessageInput();
            return;
        }
    
        UIManager.showAttendButton();
    
        ChatService.updateChatStatus(chatId, 'atendido')
            .done(data => {
            if (data.result && data.result.status === 'success') {
                $(`.chat-item[data-chat-id="${chatId}"]`).remove();
            }
            UIManager.showAttendButton();
        })
            .fail((xhr, status, error) => {
            this.handleApiError('Error al actualizar el estado del chat', error);
        });
    }
    
    handleSendMessage() {
        if (!this.selectedChatId) return;
        
        const messageBody = $('#message-input').val();
        if (messageBody.trim()) {
            MessageService.sendMessage(this.selectedChatId, messageBody)
            .done(() => {
                $('#message-input').val('');
            });
        }
    }
    
    moveToAttendedSection(chatId) {
        const chatItem = $(`.chat-item[data-chat-id="${chatId}"]`);
        
        // Handle case when chat is not in the pending section (coming from contacts)
        if (chatItem.length === 0) {
            const contactId = window.contact_id_section;
            const contactItem = $(`.contact-item[data-contact-id="${contactId}"]`);
            
            if (contactItem.length) {
            const newChatItem = this.createChatItemFromContact(contactItem, chatId);
            $('.seccion-superior').append(newChatItem);
            }
        } else {
            // Clean up existing chat item and move it
            chatItem.find('.chat-info .highlighted').remove();
            chatItem.find('.unread-count').remove();
            
            chatItem.remove();
            $('.seccion-superior').append(chatItem);
            
            // Add action buttons if not present
            this.ensureChatActionButtons(chatItem, chatId);
        }
    }
    
    moveToPendingSection(chatId, chatData) {
        const chatItem = $(`.chat-item[data-chat-id="${chatId}"]`);
        
        // Remove action buttons
        chatItem.find('.chat-close-icon').remove();
        chatItem.find('.chat-ready-icon').remove();
        
        // Add unread count if not present
        if (!chatItem.find('.unread-count').length) {
            chatItem.append(`<div class="unread-count">${chatData.unread_count}</div>`);
        }
        
        // Add last message info if not present
        if (!chatItem.find('.chat-info .highlighted').length) {
            const highlightedHtml = this.createLastMessageIndicator(
            chatData.last_message_body, 
            chatData.last_message_type
            );
            chatItem.find('.chat-info').append(highlightedHtml);
        }
        
        // Move chat to pending section
        $('.seccion-inferior').append(chatItem);
    }
    
    createChatItemFromContact(contactItem, chatId) {
        const contactColor = contactItem.data('color-contact') || '#cccccc';
        const chatIdForIcons = window.chat_id_contact_section;
        
        const newChatItem = $(`
            <div class="chat-item" data-chat-id="${chatId}" style="border-left: 5px solid ${contactColor}">
            <div class="profile-pic">
                <img src="${contactItem.find('img').attr('src')}" alt="Profile Picture"/>
            </div>
            <div class="chat-info">
                <div class="chat-name">${contactItem.find('.contact-name').text()}</div>
            </div>
            <div class="chat-close-icon" data-chat-id="${chatIdForIcons}">
                <i class="fa fa-times-circle" aria-hidden="true"></i>
            </div>
            <div class="chat-ready-icon" data-chat-id="${chatIdForIcons}">
                <i class="fa fa-check-circle" aria-hidden="true"></i>
            </div>
            </div>
        `);
        
        return newChatItem;
    }
    
    ensureChatActionButtons(chatItem, chatId) {
        if (!chatItem.find('.chat-close-icon').length) {
            chatItem.append(`
            <div class="chat-close-icon" data-chat-id="${chatId}">
                <i class="fa fa-times-circle" aria-hidden="true"></i>
            </div>
            `);
        }
        
        if (!chatItem.find('.chat-ready-icon').length) {
            chatItem.append(`
            <div class="chat-ready-icon" data-chat-id="${chatId}">
                <i class="fa fa-check-circle" aria-hidden="true"></i>
            </div>
            `);
        }
    }
    
    createLastMessageIndicator(messageBody, messageType) {
        if (messageBody.startsWith('https://') || messageBody.startsWith('http://')) {
            return '<div class="highlighted"><i class="fa fa-link message-icon" aria-hidden="true"></i><span> URL</span></div>';
        }
        
        const messageTypeIcons = {
            'image': '<i class="fa fa-image message-icon" aria-hidden="true"></i><span> Image</span>',
            'sticker': '<i class="fa fa-sticky-note message-icon" aria-hidden="true"></i><span> Sticker</span>',
            'groups_v4_invite': '<i class="fa fa-users message-icon" aria-hidden="true"></i><span> Invitación de Grupo</span>',
            'video': '<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span> Video</span>',
            'vcard': '<i class="fa fa-address-card message-icon" aria-hidden="true"></i><span> Contacto</span>',
            'location': '<i class="fa fa-map-marker message-icon" aria-hidden="true"></i><span> Ubicación</span>',
            'document': '<i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span>',
            'ptt': '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span>',
            'audio': '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span>',
            'revoked': '<i class="fa fa-ban message-icon" aria-hidden="true"></i><span>Eliminaste este mensaje</span>'
        };
        
        if (messageType in messageTypeIcons) {
            return `<div class="highlighted">${messageTypeIcons[messageType]}</div>`;
        }
        
        // Default text message
        const truncatedMessage = messageBody.length > 35 ? 
            messageBody.substring(0, 35) + '...' : 
            messageBody;
        
        return `<div class="highlighted"><span>${truncatedMessage}</span></div>`;
    }
    
    handleApiError(title, error) {
        console.error(`${title}:`, error);
        
        let errorMessage = 'Ocurrió un error inesperado. Por favor, intenta de nuevo.';
        
        if (error.responseJSON && error.responseJSON.message) {
            errorMessage = error.responseJSON.message;
        } else if (error.statusText) {
            errorMessage = error.statusText;
        }
        
        NotificationService.showError(title, errorMessage);
    }
}