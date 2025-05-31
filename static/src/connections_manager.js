document.addEventListener('DOMContentLoaded', function() {
    // Remover header y footer si existen
    document.querySelector('header')?.remove();
    document.querySelector('footer')?.remove();

    new ConnectionsManager();
});

class ConnectionsManager {
    constructor() {
        this.ws = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.setupSaveConnectionEvent();
        this.setupDeleteConnectionEvent();
        this.setupModalEvents();
    }

    setupSaveConnectionEvent() {
        const saveConnectionBtn = $('#save-connection');
        saveConnectionBtn.on('click', this.handleSaveConnection.bind(this));
    }

    validateForm() {
        const name = $('#connection_name').val().trim();
        const phoneNumber = $('#connection_phone_number').val().trim();
        const color = $('#connection_color').val();
        const countryCode = $('#country_code').val();
        
        if (!name || !phoneNumber || !color || !countryCode) {
            this.showWarningAlert('Todos los campos requeridos.');
            return false;
        }
        return true;
    }

    showWarningAlert(message) {
        Swal.fire({
            icon: 'warning', 
            title: 'Advertencia!',
            text: message,
            confirmButtonText: 'Aceptar'
        });
    }

    handleSaveConnection() {
        if (!this.validateForm()) {
            return;
        }

        const formData = this.prepareConnectionFormData();
        this.sendConnectionToServer(formData);
    }

    prepareConnectionFormData() {
        const name = $('#connection_name').val();
        const phoneNumber = $('#connection_phone_number').val();
        const color = $('#connection_color').val();
        const countryCode = $('#country_code').val();
        const fullNumber = countryCode + phoneNumber;

        const formData = new FormData();
        formData.append('name', name);
        formData.append('phone_number', fullNumber);
        formData.append('color', color);

        return formData;
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
            this.showSuccessAlert(response).then(() => {
                this.appendNewConnectionToTable(response.connection);
                const connectionModal = $('#connection-modal');
                connectionModal.modal('hide')
                this.resetConnectionForm();
            });   
        } else {
            this.showErrorAlert(response.message || 'Hubo un problema al crear la conexión.');
        }
    }

    showSuccessAlert(response) {
        return Swal.fire({
            title: 'Éxito',
            text: response.message || 'Conexión creada exitosamente.',
            icon: 'success',
            confirmButtonText: 'Aceptar'
        });
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

    resetConnectionForm() {
        $('#connection_name').val('');
        $('#connection_phone_number').val('');
        $('#connection_color').val('');
        $('#country_code').val('');
    }

    handleConnectionError(xhr) {
        const errorMessage = this.extractErrorMessage(xhr);
        this.showErrorAlert(errorMessage);
    }

    extractErrorMessage(xhr) {
        if (xhr.responseJSON && xhr.responseJSON.message) {
            return xhr.responseJSON.message;
        }
        return xhr.responseText || 'Error desconocido.';
    }

    showErrorAlert(message) {
        Swal.fire({
            title: 'Error',
            text: 'Hubo un problema al crear la conexión: ' + message,
            icon: 'error',
            confirmButtonText: 'Aceptar'
        }).then(() => {
            const connectionModal = $('#connection-modal');
            connectionModal.modal('hide')
        });
    }

    setupDeleteConnectionEvent() {
        $('.connections').on('click', '.open-modal-btn-delete', this.handleDeleteConnection.bind(this));
    }

    handleDeleteConnection(event) {
        const connectionId = $(event.currentTarget).data('connection-id');
        
        Swal.fire({
            title: '¿Estás seguro?',
            text: "No podrás revertir esto!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, eliminarla!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
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
        Swal.fire({
            title: '¡Eliminado!',
            text: 'La conexión ha sido eliminada.',
            icon: 'success',
            confirmButtonText: 'Aceptar'
        });
    }

    handleDeleteError(xhr) {
        const errorMessage = this.extractErrorMessage(xhr);
        Swal.fire({
            title: 'Error',
            text: 'Hubo un problema al eliminar la conexión: ' + errorMessage,
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
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
            this.checkClientStatus(phoneNumber).then(status => {
                if (status.isAuthenticated) {
                    // Client is already authenticated, show success message
                    Swal.fire({
                        icon: 'success',
                        title: 'Ya Autenticado',
                        text: `El número ${phoneNumber} ya está autenticado y listo para usar.`,
                        timer: 3000,
                        timerProgressBar: true
                    });
                    
                    // You might want to hide the QR code or show a "connected" message
                    const qrImg = document.getElementById("qr-code-div");
                    if (qrImg) {
                        qrImg.innerHTML = `
                            <div class="authenticated-message">
                                <i class="fa fa-check-circle" style="color: green; font-size: 48px;"></i>
                                <p>WhatsApp conectado</p>
                            </div>
                        `;
                    }
                } else {
                    // Client is not authenticated, proceed with WebSocket and QR code
                    this.openWebSocket(phoneNumber);
                    this.fetchQRCode(phoneNumber);
                }
            }).catch(error => {
                console.error("Error checking client status:", error);
                // Fallback to WebSocket and QR code in case of error
                this.openWebSocket(phoneNumber);
                this.fetchQRCode(phoneNumber);
            });
        }
    }

    checkClientStatus(phoneNumber) {
        return new Promise((resolve, reject) => {
            fetch(`http://localhost:5000/api/status_connection/${phoneNumber}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    resolve(data);
                })
                .catch(error => {
                    console.error("Error checking client status:", error);
                    reject(error);
                });
        });
    }

    handleQRModalClose() {
        const modal = document.getElementById('qr-modal');
        if (modal) {
            modal.style.display = 'none';
            this.closeWebSocket();
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

    // WebSocket and QR Code methods (from previous implementation)
    openWebSocket(phoneNumber) {
        if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
            this.ws.send(JSON.stringify({ action: "subscribe", number: phoneNumber }));
            return;
        }

        this.ws = new WebSocket("ws://localhost:5000");
        this.phoneNumber = phoneNumber; 
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
    
        this.ws.onopen = () => {
            this.reconnectAttempts = 0; // Reiniciar contador de intentos
            this.ws.send(JSON.stringify({ action: "subscribe", number: phoneNumber }));
            
            // Añadir ping para mantener la conexión viva
            this.pingInterval = setInterval(() => {
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({ action: "ping" }));
                }
            }, 75000);
        };    

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
    
                if (message.eventType === 'qrCode') {
                    const { number, qr } = message.data;
                    const receivedNumber = String(number).trim();
                    const expectedNumber = String(phoneNumber).trim();
    
                    
                    if (receivedNumber === expectedNumber && qr) {
                        this.updateQrCode(qr);
                    } else {
                        console.log('Número o QR no coinciden o QR vacío.');
                    }
                }
                else if (message.eventType === 'authenticated') {
                    const { number } = message.data;
                    
                    // Show SweetAlert notification
                    Swal.fire({
                        icon: 'success',
                        title: '¡Autenticación Exitosa!',
                        text: `El número ${number} ha sido autenticado correctamente.`,
                        timer: 6000,
                        timerProgressBar: true
                    });
                }
                else if (message.eventType === 'ready') {
                    const { number } = message.data;
                    
                    Swal.fire({
                        icon: 'info',
                        title: 'WhatsApp Listo',
                        text: `El cliente de WhatsApp para ${number} está listo para usar.`,
                        timer: 6000,
                        timerProgressBar: true
                    });
                }
            } catch (error) {
                console.error("Error al procesar mensaje WebSocket:", error);
            }
        };
    
        this.ws.onclose = () => {
            clearInterval(this.pingInterval);
            
            // Solo intentar reconectar si no hemos excedido el máximo de intentos
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                const delay = Math.min(3000 * Math.pow(1.5, this.reconnectAttempts), 30000);
                this.reconnectAttempts++;
                
                setTimeout(() => {
                    if (this.phoneNumber) {
                        this.openWebSocket(this.phoneNumber);
                    }
                }, delay);
            } else {
                console.log("Máximo de intentos de reconexión alcanzado");
            }
        };
    
        this.ws.onerror = (event) => {
            console.log("WebSocket error observed:", event);
        };
    }

    closeWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null; 
        }
    }

    fetchQRCode(number) {

        fetch(`http://localhost:5000/api/qr/${number}`)
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        setTimeout(() => this.fetchQRCode(number), 5000);
                        return null;
                    }
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (!data) return;
            
                if (data.success && data.qr) {
                    this.updateQrCode(data.qr);
                } else if (data.error) {
                    console.log("Error en respuesta:", data.error);
                }
            })
            .catch(error => {
                console.error('Error fetching QR code:', error);
            });
    }

    updateQrCode(qrText) {
        const qrImg = document.getElementById("qr-code-div");
        if (!qrImg) {
            console.error("Elemento 'qr-code-div' no encontrado.");
            return;
        }
        qrImg.innerHTML = ""; 
        new QRCode(qrImg, {
            text: qrText,
            correctLevel: QRCode.CorrectLevel.H
        });
    }
}

