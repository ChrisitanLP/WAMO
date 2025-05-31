// services/QRCodeService.js
class QRCodeService {
    constructor(webSocketService) {
        this.webSocketService = webSocketService;
        this.alertService = new AlertService();
        
        this.webSocketService.registerCallback('onQRCode', this.updateQrCode.bind(this));
        this.webSocketService.registerCallback('onAuthenticated', this.handleAuthenticated.bind(this));
        this.webSocketService.registerCallback('onReady', this.handleReady.bind(this));
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

    handleAuthenticated(data) {
        const { number } = data;
        this.alertService.showAuthenticatedAlert(number);
    }

    handleReady(data) {
        const { number } = data;
        this.alertService.showReadyAlert(number);
    }

    showAlreadyAuthenticatedMessage(phoneNumber) {
        this.alertService.showAlreadyAuthenticatedAlert(phoneNumber);
        
        const qrImg = document.getElementById("qr-code-div");
        if (qrImg) {
            qrImg.innerHTML = `
                <div class="authenticated-message">
                    <i class="fa fa-check-circle" style="color: green; font-size: 48px;"></i>
                    <p>WhatsApp conectado</p>
                </div>
            `;
        }
    }
}