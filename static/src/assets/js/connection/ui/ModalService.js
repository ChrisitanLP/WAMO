// ui/ModalService.js (continuación)
class ModalService {
    constructor() {
        this.webSocketService = new WebSocketService();
        this.qrCodeService = new QRCodeService(this.webSocketService);
    }

    setupModalEvents() {
        this.setupQRModalEvents();
        this.setupBootstrapModalEvents();
    }

    setupQRModalEvents() {
        $(document).on('click', '.open-modal-btn-qr', this.handleQRModalOpen.bind(this));
        $('.close-btn').on('click', this.handleQRModalClose.bind(this));
        
        $(window).on('click', (event) => {
            const modal = document.getElementById('qr-modal');
            if (event.target === modal) {
                this.handleQRModalClose();
            }
        });
    }

    handleQRModalOpen(event) {
        const phoneNumber = $(event.currentTarget).data('phone');
        const modal = document.getElementById('qr-modal');
        
        if (modal) {
            modal.style.display = 'block';

            // Check client status first
            this.qrCodeService.checkClientStatus(phoneNumber).then(status => {
                if (status.isAuthenticated) {
                    // Client is already authenticated, show success message
                    this.qrCodeService.showAlreadyAuthenticatedMessage(phoneNumber);
                } else {
                    // Client is not authenticated, proceed with WebSocket and QR code
                    this.webSocketService.openWebSocket(phoneNumber);
                    this.qrCodeService.fetchQRCode(phoneNumber);
                }
            }).catch(error => {
                console.error("Error checking client status:", error);
                // Fallback to WebSocket and QR code in case of error
                this.webSocketService.openWebSocket(phoneNumber);
                this.qrCodeService.fetchQRCode(phoneNumber);
            });
        }
    }

    handleQRModalClose() {
        const modal = document.getElementById('qr-modal');
        if (modal) {
            modal.style.display = 'none';
            this.webSocketService.closeWebSocket();
        }
    }

    setupBootstrapModalEvents() {
        const connectionModal = $('#connection-modal');
        const openConnectionModalBtn = $('.open-modal-btn-connection');
        const closeConnectionModalHeaderBtn = $('#close-modal-connection-header');
        const closeConnectionModalFooterBtn = $('#close-modal-connection-footer');

        if (connectionModal.length && openConnectionModalBtn.length) {
            openConnectionModalBtn.on('click', () => {
                if (navigator.appName === "Opera") {
                    connectionModal.removeClass('fade');
                } else {
                    connectionModal.modal('show');
                }
            });
    
            // Ambos botones cierran el modal
            closeConnectionModalHeaderBtn.on('click', () => connectionModal.modal('hide'));
            closeConnectionModalFooterBtn.on('click', () => connectionModal.modal('hide'));
        }
    }
}