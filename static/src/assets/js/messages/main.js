document.addEventListener('DOMContentLoaded', function() {
    // Initialize managers
    const chatManager = new ChatManager();
    const messageEditManager = new MessageEditManager();
    const dragDropManager = new DragDropManager(chatManager);
    
    // Make services globally accessible if needed
    window.ChatService = ChatService;
    window.MessageService = MessageService;
    window.FilePreviewManager = FilePreviewManager;
});