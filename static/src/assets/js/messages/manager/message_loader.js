class MessageLoader {
    constructor() {
        this.currentChatId = null;
        this.dateFormatter = new DateFormatter();
        this.messageRenderer = new MessageRenderer();
    }

    /**
     * Load messages for a specific chat
     * @param {string} chatId - The ID of the chat to load
     */
    loadMessages(chatId) {
        this.currentChatId = chatId;
        const apiUrl = `/api/messages/${chatId}`;
        const csrfToken = $('meta[name="csrf-token"]').attr('content');

        $.ajax({
            url: apiUrl,
            type: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: (data) => this.handleSuccessResponse(data),
            error: (xhr, status, error) => this.handleErrorResponse(error)
        });
    }

    /**
     * Handle successful API response
     * @param {Object} data - The response data from the API
     */
    handleSuccessResponse(data) {
        if (data && data.status === 'success') {
            this.renderSuccessfulResponse(data);
        } else if (data && data.status === 'error') {
            this.renderErrorResponse(data);
        }
    }

    /**
     * Render the chat when messages are successfully loaded
     * @param {Object} data - The response data containing messages and chat info
     */
    renderSuccessfulResponse(data) {
        const chatBannerHtml = this.messageRenderer.renderChatBanner(data.chat);
        const messagesHtml = this.messageRenderer.renderMessages(data.messages, data.chat);
        
        this.updateDOMElements(chatBannerHtml, messagesHtml);
        this.scrollToLatestMessage();
        this.updateChatStatus(data.chat);
    }

    /**
     * Render chat when API returns an error
     * @param {Object} data - Error response data
     */
    renderErrorResponse(data) {
        const chatInfo = data.chat_info || {};
        const chatBannerHtml = this.messageRenderer.renderErrorChatBanner(chatInfo);
        
        window.selectedChatId = chatInfo.id;
        
        $('.chat-banner-container').html(chatBannerHtml);
        $('#messages-container .chat-messages').html('<p class="not-messages">No se encontraron mensajes.</p>').show();
        
        this.updateChatStatus(chatInfo);
    }

    /**
     * Handle API error response
     * @param {string} error - Error message
     */
    handleErrorResponse(error) {
        console.error('AJAX error:', error);
        $('#chat-banner-container').html('<p class="not-messages">Hubo un error al cargar los mensajes.</p>');
        $('#messages-container .chat-messages').html('<p class="not-messages">No se pudieron cargar los mensajes.</p>').show();
    }

    /**
     * Update DOM elements with rendered HTML
     * @param {string} chatBannerHtml - HTML for chat banner
     * @param {string} messagesHtml - HTML for messages
     */
    updateDOMElements(chatBannerHtml, messagesHtml) {
        const $messagesContainer = $('#messages-container .chat-messages');
        const $chatBannerContainer = $('.chat-banner-container');
        
        window.loadImages();
        
        $chatBannerContainer.html(chatBannerHtml);
        $messagesContainer.html(messagesHtml).show();
    }

    /**
     * Scroll to the latest message
     */
    scrollToLatestMessage() {
        const $messagesContainer = $('#messages-container .chat-messages');
        const lastMessage = $messagesContainer.find('.message').last();
        
        if (lastMessage.length) {
            $messagesContainer.scrollTop(lastMessage.offset().top - $messagesContainer.offset().top + $messagesContainer.scrollTop());
        }
    }

    /**
     * Update chat status and UI accordingly
     * @param {Object} chatInfo - Information about the chat
     */
    updateChatStatus(chatInfo) {
        window.currentChatStatus = chatInfo.status;
        window.currentAssignedUserId = chatInfo.assigned_user_id;
        
        if (chatInfo.status === 'atendiendo' && chatInfo.assigned_user_id === window.selectedSessionId) {
            window.uiManager.showMessageInput();
        } else if (chatInfo.status === 'atendiendo' && chatInfo.assigned_user_id !== window.selectedSessionId) {
            window.uiManager.showInputDisabled();
        } else {
            window.uiManager.showAttendButton();
        }
    }
}