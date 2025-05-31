class DragDropManager {
    constructor(chatManager) {
        this.chatManager = chatManager;
        this.draggedDefaultMessageId = null;
        this.draggedProductId = null;
        this.draggingType = null;
        this.dropArea = document.getElementById('messages-container');
        
        this.init();
    }
  
    init() {
        this.setupEventListeners();
    }
  
    setupEventListeners() {
        // Prevent default drag behaviors on window
        window.addEventListener('dragover', e => e.preventDefault());
        window.addEventListener('drop', e => e.preventDefault());
        
        // Setup drag start for message items
        $(document).on('dragstart', '.message-item', this.handleMessageDragStart.bind(this));
        
        // Setup drag start for product items
        $(document).on('dragstart', '.product-item', this.handleProductDragStart.bind(this));
        
        // Setup drop area events
        this.dropArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.dropArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.dropArea.addEventListener('drop', this.handleDrop.bind(this));
    }
  
    handleMessageDragStart(event) {
        this.draggedDefaultMessageId = $(event.currentTarget).data('message-id');
        this.draggedProductId = null;
        this.draggingType = 'defaultMessage';
    }
  
    handleProductDragStart(event) {
        this.draggedProductId = $(event.currentTarget).data('product-id');
        this.draggedDefaultMessageId = null;
        this.draggingType = 'product';
    }
  
    handleDragOver(event) {
        event.preventDefault();
        this.dropArea.classList.add('drag-over');
    }
  
    handleDragLeave() {
        this.dropArea.classList.remove('drag-over');
    }
  
    handleDrop(event) {
        event.preventDefault();
        this.dropArea.classList.remove('drag-over');
    
        const chatId = this.chatManager.selectedChatId;
    
        if (!chatId) {
            console.log('No se ha seleccionado un chat.');
            return;
        }
    
        // Check if input is enabled and the chat is being attended by current user
        if (window.currentChatStatus !== 'atendiendo' || window.currentAssignedUserId !== this.chatManager.selectedSessionId) {
            return;
        }
    
        // Process based on drag type
        if (this.draggingType === 'defaultMessage' && this.draggedDefaultMessageId) {
            MessageService.sendDefaultMessage(chatId, this.draggedDefaultMessageId);
        } else if (this.draggingType === 'product' && this.draggedProductId) {
            MessageService.sendProductMessage(chatId, this.draggedProductId);
        }
    
        // Reset drag state
        this.resetDragState();
    }
  
    resetDragState() {
        this.draggedDefaultMessageId = null;
        this.draggedProductId = null;
        this.draggingType = null;
    }
}