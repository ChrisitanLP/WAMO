// services/WebSocketService.js
class WebSocketService {
    constructor() {
        this.ws = null;
        this.phoneNumber = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.pingInterval = null;
        this.callbacks = {
            onQRCode: null,
            onAuthenticated: null,
            onReady: null
        };
    }

    registerCallback(eventType, callback) {
        if (this.callbacks.hasOwnProperty(eventType)) {
            this.callbacks[eventType] = callback;
        }
    }

    openWebSocket(phoneNumber) {
        if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
            this.ws.send(JSON.stringify({ action: "subscribe", number: phoneNumber }));
            return;
        }

        this.ws = new WebSocket("ws://localhost:5000");
        this.phoneNumber = phoneNumber; 
        this.reconnectAttempts = 0;
    
        this.ws.onopen = () => {
            this.reconnectAttempts = 0;
            this.ws.send(JSON.stringify({ action: "subscribe", number: phoneNumber }));
            
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
    
                    if (receivedNumber === expectedNumber && qr && this.callbacks.onQRCode) {
                        this.callbacks.onQRCode(qr);
                    }
                }
                else if (message.eventType === 'authenticated' && this.callbacks.onAuthenticated) {
                    this.callbacks.onAuthenticated(message.data);
                }
                else if (message.eventType === 'ready' && this.callbacks.onReady) {
                    this.callbacks.onReady(message.data);
                }
            } catch (error) {
                console.error("Error al procesar mensaje WebSocket:", error);
            }
        };
    
        this.ws.onclose = () => {
            clearInterval(this.pingInterval);
            
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
}