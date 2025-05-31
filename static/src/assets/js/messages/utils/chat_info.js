class ChatInfoManager {
    constructor() {
        this.currentChatId = null;
        this.currentChatStatus = null;
        this.currentAssignedUserId = null;
    }
    
    /**
     * Update current chat information
     * @param {string} chatId - Chat ID
     * @param {string} status - Chat status
     * @param {string} assignedUserId - ID of assigned user
     */
    updateChatInfo(chatId, status, assignedUserId) {
        this.currentChatId = chatId;
        this.currentChatStatus = status;
        this.currentAssignedUserId = assignedUserId;
        
        // Make info available globally
        window.currentChatId = chatId;
        window.currentChatStatus = status;
        window.currentAssignedUserId = assignedUserId;
    }
    
    /**
     * Get current chat information
     * @returns {Object} Current chat information
     */
    getChatInfo() {
        return {
            chatId: this.currentChatId,
            status: this.currentChatStatus,
            assignedUserId: this.currentAssignedUserId
        };
    }
}