class UIManager {
    constructor() {
        this.initReplyContainer();
    }

    /**
     * Show the message input field (when chat is assigned to current user)
     */
    showMessageInput() {
        $('#message-input-container').show();
        $('#attend-button-container').hide();
        $('#input-disabled-container').hide();
        $('#message-input').focus();
    }
    
    /**
     * Show the input disabled message (when chat is assigned to another user)
     */
    showInputDisabled() {
        $('#message-input-container').hide();
        $('#attend-button-container').hide();
        $('#input-disabled-container').show();
    }
    
    /**
     * Show the attend button (when chat is not assigned to any user)
     */
    showAttendButton() {
        $('#message-input-container').hide();
        $('#attend-button-container').show();
        $('#input-disabled-container').hide();
    }

    /**
     * Initialize message loading for a chat
     * @param {string} chatId - Chat ID to load
     */
    loadChat(chatId) {
        this.messageLoader.loadMessages(chatId);
    }

    /**
     * Initialize reply container functionality
     */
    initReplyContainer() {
        window.showReplyContainer = function() {
            UIManager.updateScrollButtonPosition();
            const replyContainer = document.getElementById('reply-container');
            replyContainer.style.display = 'flex';
            setTimeout(() => {
                replyContainer.classList.add('show');
            }, 10);
        };
        
        window.hideReplyContainer = function() {
            UIManager.updateScrollButtonPosition();
            const replyContainer = document.getElementById('reply-container');
            replyContainer.classList.remove('show');
            setTimeout(() => {
                replyContainer.style.display = 'none';
            }, 300);
        };
    }

    /**
     * Update the position of the scroll button
     */
    static updateScrollButtonPosition() {
        // Implementation would adjust the scroll button position
        // based on whether the reply container is shown or hidden
        const scrollButton = document.getElementById('scroll-bottom-btn');
        const replyContainer = document.getElementById('reply-container');
        
        if (scrollButton && replyContainer) {
            const isReplyVisible = replyContainer.classList.contains('show');
            const bottomPosition = isReplyVisible ? '120px' : '70px';
            scrollButton.style.bottom = bottomPosition;
        }
    }
}