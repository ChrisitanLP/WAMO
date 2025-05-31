class MessageService {
    
    static sendMessage(chatId, messageText) {
        const csrfToken = $('meta[name="csrf-token"]').attr('content');
        
        return $.ajax({
            url: '/api/message/send',
            type: 'POST',
            headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
            },
            data: JSON.stringify({
            chat_id: chatId,
            message: messageText
            })
        })
        .done(() => {
            this.loadMessages(chatId);
        })
        .fail((xhr, status, error) => {
            console.error('Error sending message:', error);
        });
    }
  
    static sendDefaultMessage(chatId, defaultId) {
        const csrfToken = $('meta[name="csrf-token"]').attr('content');
        
        return $.ajax({
            url: '/api/message/send-default-messages',
            type: 'POST',
            headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
            },
            data: JSON.stringify({
            chat_id: chatId,
            default_id: defaultId
            })
        })
        .done(data => {
            if (data.status === 'success') {
            this.loadMessages(chatId);
            } else {
            console.error('Error al enviar el mensaje por defecto:', data.message);
            }
        })
        .fail((xhr, status, error) => {
            console.error('Error en la solicitud:', error);
        });
    }
  
    static sendProductMessage(chatId, productId) {
        const csrfToken = $('meta[name="csrf-token"]').attr('content');
        
        return $.ajax({
            url: '/api/message/send-product',
            type: 'POST',
            headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
            },
            data: JSON.stringify({
            chat_id: chatId,
            product_id: productId
            })
        })
        .done(data => {
            if (data.result && data.result.status === 'success') {
            this.loadMessages(chatId);
            } else {
            console.error('Error al enviar el producto:', data.message);
            }
        })
        .fail((xhr, status, error) => {
            console.error('Error en la solicitud:', error);
        });
    }
  
    static editMessage(messageId, newContent) {
        return $.ajax({
            url: '/api/message/edit',
            type: 'POST',
            data: JSON.stringify({ messageId, newContent }),
            contentType: 'application/json'
        });
    }

    /**
     * Send a text message
     * @param {string} chatId - ID of the chat
     * @param {string} text - Message text
     * @param {string} replyToMessageId - ID of the message being replied to (optional)
     */
    static sendTextMessage(chatId, text, replyToMessageId = null) {
        const messageData = {
            chat_id: chatId,
            text: text
        };
        
        if (replyToMessageId) {
            messageData.reply_to_message_id = replyToMessageId;
        }
        
        $.ajax({
            url: '/api/message/send',
            type: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
            },
            data: JSON.stringify(messageData),
            success: (data) => {
                if (data.status === 'success') {
                    // Clear input and reload messages
                    $('#message-input').val('');
                    MessageService.loadMessages(chatId);
                    
                    // Clear reply if there was one
                    if (replyToMessageId) {
                        window.messageManager.handleCancelReply();
                    }
                } else {
                    console.error('Error sending message:', data.message);
                    NotificationService.showError('Error', 'No se pudo enviar el mensaje.');
                }
            },
            error: (xhr, status, error) => {
                console.error('Error sending message:', error);
                NotificationService.showError('Error', 'No se pudo enviar el mensaje.');
            }
        });
    }
}
  