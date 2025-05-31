$(document).ready(function () {
    // Usar IIFE para evitar contaminación del espacio global
    const chatFileHandler = new ChatFileHandler();
    
    // Exponer funciones necesarias al ámbito global
    window.previewImageOrVideo = chatFileHandler.previewMediaFile.bind(chatFileHandler);
    window.previewDocumentFile = chatFileHandler.previewDocumentFile.bind(chatFileHandler);
    window.sendFile = chatFileHandler.sendFile.bind(chatFileHandler);
});

/**
 * ChatFileHandler - Módulo para gestionar la funcionalidad de archivos en la aplicación de chat
 * Implementa patrones de diseño modular, programación orientada a objetos y manejo asíncrono
 */
class ChatFileHandler {
    constructor() {
        // Elementos UI principales
        this.elements = {
            plusBtn: document.getElementById('plus-btn'),
            closePlusPickerBtn: document.getElementById('close-plus-picker'),
            plusPicker: document.getElementById('plus-picker'),
            plusPickerBody: document.getElementById('plus-picker-body'),
            emojiPicker: document.getElementById('emoji-picker'),
            stickerPicker: document.getElementById('sticker-picker'),
            filePreview: document.getElementById('file-preview'),
            closeFilePreviewBtn: document.getElementById('close-file-preview'),
            previewImage: document.getElementById('preview-image'),
            previewVideo: document.getElementById('preview-video'),
            previewDocument: document.getElementById('preview-document'),
            fileMessage: document.getElementById('file-message'),
            sendFileBtn: document.getElementById('send-file')
        };

        // Estado de la aplicación
        this.state = {
            selectedChatId: null,
            selectedFile: null
        };

        // Configuración de opciones de archivos
        this.fileOptions = [
            { id: 'photos-videos', icon: 'fa-camera', label: 'Fotos y Videos', accept: 'image/*,video/*' },
            { id: 'documents', icon: 'fa-file', label: 'Documentos', accept: '*/*' }
        ];

        // Mapa de tipos de archivo a clases de iconos
        this.fileIconMap = {
            default: 'fa-file-alt',
            pdf: 'fa-file-pdf-o',
            word: 'fa-file-word-o',
            excel: 'fa-file-excel-o',
            powerpoint: 'fa-file-powerpoint-o'
        };

        // Inicializar la aplicación
        this.init();
    }

    /**
     * Inicializa la aplicación adjuntando eventos
     */
    init() {
        // Verificar que los elementos existan antes de adjuntar eventos
        this.validateElements();
        this.attachEventListeners();
        
        // Exponer métodos necesarios globalmente (mejor sería usar eventos personalizados)
        window.toggleFilePreview = this.toggleFilePreview.bind(this);
    }

    /**
     * Valida que los elementos críticos existan en el DOM
     */
    validateElements() {
        const requiredElements = ['plusBtn', 'plusPicker', 'filePreview'];
        for (const element of requiredElements) {
            if (!this.elements[element]) {
                console.warn(`Elemento requerido "${element}" no encontrado en el DOM`);
            }
        }
    }

    /**
     * Adjunta todos los escuchadores de eventos
     */
    attachEventListeners() {
        // Manejar evento de clic en el botón plus
        if (this.elements.plusBtn) {
            this.elements.plusBtn.addEventListener('click', this.handlePlusButtonClick.bind(this));
        }

        // Manejar cierre de picker
        if (this.elements.closePlusPickerBtn) {
            this.elements.closePlusPickerBtn.addEventListener('click', this.handleClosePlusPickerClick.bind(this));
        }

        // Manejar cierre de vista previa
        if (this.elements.closeFilePreviewBtn) {
            this.elements.closeFilePreviewBtn.addEventListener('click', this.handleCloseFilePreviewClick.bind(this));
        }

        // Manejar envío de archivo
        if (this.elements.sendFileBtn) {
            this.elements.sendFileBtn.addEventListener('click', this.handleSendFileClick.bind(this));
        }

        // Manejar selección de chat
        $(document).on('click', '.chat-item', (event) => {
            this.state.selectedChatId = $(event.currentTarget).data('chat-id');
        });

        // Cerrar pickers al hacer clic en otros elementos
        $(document).on('click', (event) => {
            const isPlusBtn = $(event.target).closest(this.elements.plusBtn).length > 0;
            const isPlusPicker = $(event.target).closest(this.elements.plusPicker).length > 0;
            const isFilePreview = $(event.target).closest(this.elements.filePreview).length > 0;

            if (!isPlusBtn && !isPlusPicker && !isFilePreview) {
                this.closeAllPickers();
            }
        });
    }

    /**
     * Maneja el clic en el botón plus para mostrar/ocultar opciones
     */
    handlePlusButtonClick() {
        const { plusPicker, plusBtn } = this.elements;
        
        if (plusPicker.style.display === 'none' || plusPicker.style.display === '') {
            this.closeAllPickers();
            this.loadPlusOptions();
            plusPicker.style.display = 'block';
            plusBtn.innerHTML = '<i class="fa fa-times message-icon" aria-hidden="true"></i>';
        } else {
            plusPicker.style.display = 'none';
            plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
        }
    }

    /**
     * Maneja el clic en el botón de cierre del picker
     */
    handleClosePlusPickerClick() {
        const { plusPicker, plusBtn } = this.elements;
        if (plusPicker) {
            plusPicker.style.display = 'none';
            plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
        }
    }

    /**
     * Maneja el clic en el botón de cierre de la vista previa
     */
    handleCloseFilePreviewClick() {
        this.closeAllPickers();
        const { plusPicker, plusBtn } = this.elements;
        plusPicker.style.display = 'none';
        plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
    }

    /**
     * Maneja el clic en el botón de envío de archivo
     */
    handleSendFileClick() {
        const { fileMessage } = this.elements;
        const { selectedChatId, selectedFile } = this.state;
        
        if (!selectedChatId) {
            this.showNotification('error', 'Error', 'No se ha seleccionado ningún chat');
            return;
        }
        
        this.sendFile(selectedChatId, selectedFile, fileMessage.value);
    }

    /**
     * Cierra todos los pickers y previsualización
     */
    closeAllPickers() {
        const { plusPicker, plusBtn, stickerPicker, emojiPicker } = this.elements;
        
        if (plusPicker) {
            plusPicker.style.display = 'none';
            plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
        }
        
        if (stickerPicker) {
            stickerPicker.style.display = 'none';
        }
        
        if (emojiPicker) {
            emojiPicker.style.display = 'none';
        }
        
        this.toggleFilePreview(false);
    }

    /**
     * Carga las opciones del menú plus de forma dinámica
     */
    loadPlusOptions() {
        const { plusPickerBody } = this.elements;
        
        if (!plusPickerBody) return;
        
        // Limpia el contenedor
        plusPickerBody.innerHTML = '';

        // Crea y agrega cada opción
        this.fileOptions.forEach(option => {
            const optionDiv = document.createElement('div');
            optionDiv.classList.add('plus-option');
            optionDiv.id = option.id;

            const optionIcon = document.createElement('i');
            optionIcon.classList.add('fa', option.icon, 'plus-option-icon');
            optionDiv.appendChild(optionIcon);

            const optionLabel = document.createElement('span');
            optionLabel.classList.add('plus-option-label');
            optionLabel.textContent = option.label;
            optionDiv.appendChild(optionLabel);

            plusPickerBody.appendChild(optionDiv);

            // Agrega evento de clic a la opción
            optionDiv.addEventListener('click', () => {
                this.handleFileSelection(option.accept);
            });
        });
    }

    /**
     * Maneja la selección de archivos
     * @param {string} accept - Tipos de archivo aceptados
     */
    handleFileSelection(accept) {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = accept;
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);

        // Agrega evento para manejar el cambio
        fileInput.addEventListener('change', (event) => {
            if (event.target.files && event.target.files.length > 0) {
                this.state.selectedFile = event.target.files[0];
                
                if (accept === 'image/*,video/*') {
                    this.previewMediaFile(this.state.selectedFile);
                } else {
                    this.previewDocumentFile(this.state.selectedFile);
                }
            }
        });

        // Simula clic en el input para abrir diálogo de selección
        fileInput.click();
        
        // Limpia el input después de usarlo
        setTimeout(() => {
            document.body.removeChild(fileInput);
        }, 1000);
    }

    /**
     * Previsualiza archivos de imagen o video
     * @param {File} file - Archivo a previsualizar
     */
    previewMediaFile(file) {
        if (!file) return;
        
        const { previewImage, previewVideo, previewDocument } = this.elements;
        const fileType = file.type.split('/')[0];
        const fileUrl = URL.createObjectURL(file);

        // Oculta todas las previsualizaciones
        previewImage.style.display = 'none';
        previewVideo.style.display = 'none';
        previewDocument.style.display = 'none';

        // Muestra la previsualización adecuada
        if (fileType === 'image') {
            previewImage.src = fileUrl;
            previewImage.style.display = 'block';
        } else if (fileType === 'video') {
            previewVideo.src = fileUrl;
            previewVideo.style.display = 'block';
        }

        // Muestra la previsualización
        this.toggleFilePreview(true);
        
        // Libera la URL del objeto cuando ya no se necesite
        this.cleanupObjectUrl(fileUrl);
    }

    /**
     * Libera recursos de URL.createObjectURL
     * @param {string} url - URL a limpiar
     */
    cleanupObjectUrl(url) {
        // Esperar un tiempo razonable antes de revocar la URL
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 5000);
    }

    /**
     * Previsualiza documentos
     * @param {File} file - Archivo a previsualizar
     */
    previewDocumentFile(file) {
        if (!file) return;
        
        const { previewImage, previewVideo, previewDocument } = this.elements;
        
        // Oculta todas las previsualizaciones
        previewImage.style.display = 'none';
        previewVideo.style.display = 'none';
        previewDocument.style.display = 'block';

        // Determina el icono apropiado para el tipo de archivo
        const fileType = file.type.split('/')[1] || '';
        let iconClass = this.fileIconMap.default;

        if (fileType === 'pdf') {
            iconClass = this.fileIconMap.pdf;
        } else if (fileType.includes('word')) {
            iconClass = this.fileIconMap.word;
        } else if (fileType.includes('excel')) {
            iconClass = this.fileIconMap.excel;
        } else if (fileType.includes('powerpoint')) {
            iconClass = this.fileIconMap.powerpoint;
        }

        // Crea la previsualización del documento
        previewDocument.innerHTML = `
            <div class="document-preview">
                <i class="fa ${iconClass} document-icon"></i>
                <span class="document-name">${this.sanitizeHTML(file.name)}</span>
            </div>
        `;

        // Muestra la previsualización
        this.toggleFilePreview(true);
    }

    /**
     * Sanea texto para prevenir XSS
     * @param {string} text - Texto a sanear
     * @return {string} Texto saneado
     */
    sanitizeHTML(text) {
        const element = document.createElement('div');
        element.textContent = text;
        return element.innerHTML;
    }

    /**
     * Alterna la visibilidad de la previsualización de archivos
     * @param {boolean} visible - Indica si debe mostrarse
     */
    toggleFilePreview(visible) {
        const filePreview = $(this.elements.filePreview);
        
        if (visible) {
            filePreview.css('display', 'flex');
            setTimeout(() => {
                filePreview.addClass('visible');
            }, 10); // Pequeño retraso para permitir que el navegador procese el cambio de display
        } else {
            filePreview.removeClass('visible');
            
            // Espera a que termine la animación
            setTimeout(() => {
                filePreview.css('display', 'none');
            }, 300);
        }
    }

    /**
     * Envía un archivo al chat seleccionado
     * @param {string} chatId - ID del chat
     * @param {File} file - Archivo a enviar
     * @param {string} messageBody - Mensaje que acompaña al archivo
     * @return {Promise} Promesa que se resuelve cuando el archivo se ha enviado
     */
    sendFile(chatId, file, messageBody) {
        return new Promise((resolve, reject) => {
            if (!file) {
                this.showNotification('error', 'Error', 'No se seleccionó ningún archivo');
                reject(new Error('No se seleccionó ningún archivo'));
                return;
            }

            if (!chatId) {
                this.showNotification('error', 'Error', 'No se ha seleccionado un chat');
                reject(new Error('No se ha seleccionado un chat'));
                return;
            }

            const fileName = file.name;
            const reader = new FileReader();
            
            reader.onload = (e) => {
                try {
                    const fileContent = e.target.result.split(',')[1];
                    
                    // Enviar archivo al servidor usando fetch o axios para mayor modernidad
                    this.sendFileToServer(chatId, fileName, fileContent, messageBody)
                        .then(response => {
                            this.handleFileSendResponse(response, chatId);
                            resolve(response);
                        })
                        .catch(error => {
                            this.showNotification('error', 'Error', `Error al enviar archivo: ${error.message}`);
                            reject(error);
                        });
                } catch (error) {
                    this.showNotification('error', 'Error', `Error al procesar archivo: ${error.message}`);
                    reject(error);
                }
            };

            reader.onerror = (error) => {
                this.showNotification('error', 'Error', `Error al leer archivo: ${error.message || 'Error desconocido'}`);
                reject(error);
            };

            reader.readAsDataURL(file);
        });
    }

    /**
     * Envía el archivo al servidor
     * @param {string} chatId - ID del chat
     * @param {string} fileName - Nombre del archivo
     * @param {string} fileContent - Contenido del archivo codificado en base64
     * @param {string} messageBody - Mensaje que acompaña al archivo
     * @return {Promise} Promesa con la respuesta del servidor
     */
    sendFileToServer(chatId, fileName, fileContent, messageBody) {
        const payload = {
            chatId,
            file_name: fileName,
            file_content: fileContent,
            messageBody
        };

        // Uso de fetch para modernizar el código (también se podría usar axios)
        return fetch('/send_file_path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        });
    }

    /**
     * Maneja la respuesta del servidor al enviar un archivo
     * @param {Object} response - Respuesta del servidor
     * @param {string} chatId - ID del chat
     */
    handleFileSendResponse(response, chatId) {
        const { previewImage, previewVideo, previewDocument, fileMessage } = this.elements;
        
        if (response.result && response.result.status === 'success') {
            this.showNotification('success', 'Éxito', 'Archivo enviado con éxito');
            
            // Limpiar previsualización y mensaje
            previewImage.src = '';
            previewImage.style.display = 'none';
            previewVideo.src = '';
            previewVideo.style.display = 'none';
            previewDocument.innerHTML = '';
            previewDocument.style.display = 'none';
            fileMessage.value = '';
            
            // Ocultar previsualización
            this.toggleFilePreview(false);
            
            // Recargar mensajes si la función existe
            if (typeof window.loadMessages === 'function') {
                window.loadMessages(chatId);
            }
            
            // Limpiar estado
            this.state.selectedFile = null;
        } else {
            const errorMessage = response.result ? response.result.message : 'Error desconocido';
            this.showNotification('error', 'Error', `Error al enviar archivo: ${errorMessage}`);
        }
    }

    /**
     * Muestra una notificación usando SweetAlert2
     * @param {string} icon - Tipo de notificación (success, error, warning, info)
     * @param {string} title - Título de la notificación
     * @param {string} text - Texto de la notificación
     */
    showNotification(icon, title, text) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon,
                title,
                text,
                confirmButtonText: 'Aceptar'
            });
        } else {
            console.log(`${title}: ${text}`);
        }
    }
}