// managers/ConnectionsManager.js
class ConnectionsManager {
    constructor() {
        this.alertService = new AlertService();
        this.modalService = new ModalService();
        this.webSocketService = new WebSocketService();
        this.qrCodeService = new QRCodeService(this.webSocketService);
        this.formUtils = new FormUtils();
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.setupSaveConnectionEvent();
        this.setupDeleteConnectionEvent();
        this.modalService.setupModalEvents();
    }

    setupSaveConnectionEvent() {
        const saveConnectionBtn = $('#save-connection');
        saveConnectionBtn.on('click', this.handleSaveConnection.bind(this));
    }

    handleSaveConnection() {
        if (!this.formUtils.validateForm()) {
            return;
        }

        const formData = this.formUtils.prepareConnectionFormData();
        this.sendConnectionToServer(formData);
    }

    sendConnectionToServer(formData) {
        $.ajax({
            url: '/api/connection/add',
            method: 'POST',
            contentType: false,
            processData: false,
            data: formData,
            success: this.handleConnectionSuccess.bind(this),
            error: this.handleConnectionError.bind(this)
        });
    }

    handleConnectionSuccess(response) {
        if (response.success) {
            this.alertService.showSuccessAlert(response).then(() => {
                this.appendNewConnectionToTable(response.connection);
                const connectionModal = $('#connection-modal');
                connectionModal.modal('hide')
                this.formUtils.resetConnectionForm();
            });   
        } else {
            this.alertService.showErrorAlert(response.message || 'Hubo un problema al crear la conexión.');
        }
    }

    appendNewConnectionToTable(connection) {
        $('.connections tbody').append(`
            <tr data-connection-id="${connection.id}">
                <td>${connection.id}</td>
                <td>${connection.name}</td>
                <td>${connection.phone_number}</td>
                <td><span class="color-box" style="background-color: ${connection.color}"></span></td>
                <td>
                    <button class="qr-button open-modal-btn-qr" data-phone="${connection.phone_number}">
                        <i class="fa fa-qrcode" aria-hidden="true"></i>
                    </button>
                </td>
                <td>
                    <button class="delete-button open-modal-btn-delete" data-connection-id="${connection.id}">
                        <i class="fa fa-trash" aria-hidden="true"></i>
                    </button>
                </td>
            </tr>
        `);
    }

    handleConnectionError(xhr) {
        const errorMessage = this.formUtils.extractErrorMessage(xhr);
        this.alertService.showErrorAlert(errorMessage);
    }

    setupDeleteConnectionEvent() {
        $('.connections').on('click', '.open-modal-btn-delete', this.handleDeleteConnection.bind(this));
    }

    handleDeleteConnection(event) {
        const connectionId = $(event.currentTarget).data('connection-id');
        
        this.alertService.showConfirmDeleteAlert().then((result) => {
            if (result.isConfirmed) {
                this.sendDeleteRequest(connectionId);
            }
        });
    }

    sendDeleteRequest(connectionId) {
        $.ajax({
            url: `/api/connection/delete/${connectionId}`,
            method: 'POST',
            success: () => this.handleDeleteSuccess(connectionId),
            error: this.handleDeleteError.bind(this)
        });
    }

    handleDeleteSuccess(connectionId) {
        $(`tr[data-connection-id="${connectionId}"]`).remove();
        this.alertService.showDeleteSuccessAlert();
    }

    handleDeleteError(xhr) {
        const errorMessage = this.formUtils.extractErrorMessage(xhr);
        this.alertService.showDeleteErrorAlert(errorMessage);
    }
}