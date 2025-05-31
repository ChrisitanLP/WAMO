document.addEventListener('DOMContentLoaded', function() {
    const stickerManager = new StickerManager();
    stickerManager.init();
    
    // Exponer la instancia para uso externo si es necesario
    window.stickerManager = stickerManager;
});


/**
 * Clase principal para la gestión de stickers
 */
class StickerManager {
    /**
     * Constructor de la clase StickerManager
     */
    constructor() {
        // Referencias a elementos DOM
        this.elements = {
            stickerBtn: document.getElementById('sticker-btn'),
            closeStickerPickerBtn: document.getElementById('close-sticker-picker'),
            stickerPicker: document.getElementById('sticker-picker'),
            stickerPickerBody: document.getElementById('sticker-picker-body'),
            emojiPicker: document.getElementById('emoji-picker'),
            plusPicker: document.getElementById('plus-picker'),
            plusBtn: document.getElementById('plus-btn')
        };

        // Atributos
        this.selectedChatId = null;
        this.stickerFileInput = null;
        this.initialized = false;
    }

    /**
     * Inicializa el gestor de stickers
     * @returns {StickerManager} - Instancia actual para encadenamiento
     */
    init() {
        if (this.initialized) return this;

        this.createFileInput();
        this.setupEventListeners();
        this.initialized = true;
        
        console.log('StickerManager inicializado correctamente');
        return this;
    }

    /**
     * Crea y configura el input para subir stickers
     */
    createFileInput() {
        // Crear y configurar el elemento input file
        this.stickerFileInput = document.createElement('input');
        this.stickerFileInput.type = 'file';
        this.stickerFileInput.id = 'sticker-file-input';
        this.stickerFileInput.accept = 'image/webp';
        this.stickerFileInput.style.display = 'none';
        document.body.appendChild(this.stickerFileInput);
        
        // Añadir el evento de cambio al input
        this.stickerFileInput.addEventListener('change', this.handleFileUpload.bind(this));
    }

    /**
     * Configura todos los event listeners
     */
    setupEventListeners() {
        // Event listener para cerrar pickers al hacer click fuera
        document.addEventListener('click', this.handleOutsideClick.bind(this));
        
        // Configurar botón de stickers
        if (this.elements.stickerBtn) {
            this.elements.stickerBtn.addEventListener('click', this.toggleStickerPicker.bind(this));
        }
        
        // Configurar botón para cerrar el selector de stickers
        if (this.elements.closeStickerPickerBtn) {
            this.elements.closeStickerPickerBtn.addEventListener('click', () => this.closePicker('stickerPicker'));
        }
        
        // Escuchar clics en chats para obtener el ID del chat seleccionado
        $(document).on('click', '.chat-item', this.handleChatSelection.bind(this));
    }

    /**
     * Maneja clics fuera del picker para cerrarlo
     * @param {Event} e - Evento de clic
     */
    handleOutsideClick(e) {
        if (this.elements.stickerPicker && 
            this.elements.stickerPicker.style.display === 'block' && 
            !$(e.target).closest('#sticker-picker, #sticker-btn').length) {
            this.closePicker('stickerPicker');
        }
    }

    /**
     * Registra el ID del chat seleccionado
     * @param {Event} e - Evento de clic
     */
    handleChatSelection(e) {
        this.selectedChatId = $(e.currentTarget).data('chat-id');
    }

    /**
     * Alterna la visibilidad del selector de stickers
     */
    toggleStickerPicker() {
        const { stickerPicker } = this.elements;
        
        if (!stickerPicker) return;
        
        const isHidden = stickerPicker.style.display === 'none' || stickerPicker.style.display === '';
        
        if (isHidden) {
            this.closeAllPickers();
            this.loadStickers();
            stickerPicker.style.display = 'block';
        } else {
            stickerPicker.style.display = 'none';
        }
    }

    /**
     * Cierra todos los pickers abiertos
     */
    closeAllPickers() {
        const { stickerPicker, emojiPicker, plusPicker, plusBtn } = this.elements;
        
        if (stickerPicker) stickerPicker.style.display = 'none';
        if (emojiPicker) emojiPicker.style.display = 'none';
        if (plusPicker) plusPicker.style.display = 'none';
        
        if (plusBtn) {
            plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
        }
    }

    /**
     * Cierra un picker específico
     * @param {string} pickerName - Nombre del picker a cerrar
     */
    closePicker(pickerName) {
        if (this.elements[pickerName]) {
            this.elements[pickerName].style.display = 'none';
        }
    }

    /**
     * Carga los stickers desde la API
     * @returns {Promise} - Promesa que se resuelve cuando se cargan los stickers
     */
    loadStickers() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/sticker',
                method: 'GET',
                dataType: 'json',
                success: (data) => {
                    if (Array.isArray(data)) {
                        this.renderStickers(data);
                        resolve(data);
                    } else {
                        reject(new Error('Invalid sticker data format'));
                    }
                },
                error: (xhr, status, error) => {
                    console.error('Error loading stickers:', error);
                    reject(error);
                }
            });
        });
    }

    /**
     * Renderiza los stickers en el selector
     * @param {Array} stickers - Array de objetos sticker
     */
    renderStickers(stickers) {
        const { stickerPickerBody } = this.elements;
        
        if (!stickerPickerBody) return;
        
        // Limpiar contenido actual
        stickerPickerBody.innerHTML = '';
        
        // Crear fragmento para optimizar el rendimiento
        const fragment = document.createDocumentFragment();
        
        // Añadir botón para agregar stickers
        const addStickerDiv = this.createAddStickerButton();
        fragment.appendChild(addStickerDiv);
        
        // Añadir stickers existentes
        stickers.forEach(sticker => {
            const stickerElement = this.createStickerElement(sticker);
            fragment.appendChild(stickerElement);
        });
        
        // Añadir todos los elementos de una vez para mejor rendimiento
        stickerPickerBody.appendChild(fragment);
    }

    /**
     * Crea el botón para añadir nuevos stickers
     * @returns {HTMLElement} - Elemento DOM del botón
     */
    createAddStickerButton() {
        const addStickerDiv = document.createElement('div');
        addStickerDiv.classList.add('sticker', 'sticker-image');
        addStickerDiv.id = 'add-sticker-btn';

        const addStickerIcon = document.createElement('i');
        addStickerIcon.classList.add('fa', 'fa-plus', 'sticker-add-icon');
        addStickerIcon.style.fontSize = '50px';

        addStickerDiv.appendChild(addStickerIcon);
        
        // Añadir evento para abrir el selector de archivos
        addStickerDiv.addEventListener('click', () => {
            if (this.stickerFileInput) {
                this.stickerFileInput.click();
            }
        });
        
        return addStickerDiv;
    }

    /**
     * Crea un elemento sticker individual
     * @param {Object} sticker - Objeto con la información del sticker
     * @returns {HTMLElement} - Elemento DOM del sticker
     */
    createStickerElement(sticker) {
        const stickerDiv = document.createElement('div');
        stickerDiv.classList.add('sticker');
        stickerDiv.dataset.stickerId = sticker.id;

        // Imagen del sticker
        const stickerImg = document.createElement('img');
        stickerImg.src = sticker.sticker_url;
        stickerImg.alt = sticker.name;
        stickerImg.title = sticker.name;
        stickerImg.classList.add('sticker-image');
        stickerImg.addEventListener('click', () => this.handleStickerClick(sticker));

        // Botón para eliminar el sticker
        const closeBtn = document.createElement('button');
        closeBtn.classList.add('sticker-close-btn');
        closeBtn.innerHTML = '<i class="fa fa-times"></i>';
        closeBtn.dataset.stickerId = sticker.id;
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Evitar que el clic se propague al sticker
            this.handleStickerDelete(sticker.id);
        });

        stickerDiv.appendChild(stickerImg);
        stickerDiv.appendChild(closeBtn);
        
        return stickerDiv;
    }

    /**
     * Maneja el clic en un sticker para enviarlo
     * @param {Object} sticker - Objeto con la información del sticker
     */
    handleStickerClick(sticker) {
        if (!this.selectedChatId) {
            this.showAlert('Error', 'No hay chat seleccionado', 'error');
            return;
        }
        
        this.sendSticker(this.selectedChatId, sticker.sticker_url, sticker.file_name);
        this.closePicker('stickerPicker');
    }

    /**
     * Muestra un diálogo de confirmación para eliminar un sticker
     * @param {string|number} stickerId - ID del sticker a eliminar
     */
    handleStickerDelete(stickerId) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "¡No podrás revertir esto!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, eliminarlo',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                this.deleteSticker(stickerId);
            }
        });
    }

    /**
     * Realiza la petición para eliminar un sticker
     * @param {string|number} stickerId - ID del sticker a eliminar
     */
    deleteSticker(stickerId) {
        $.ajax({
            url: `/api/sticker/delete/${stickerId}`,
            method: 'DELETE',
            success: (response) => {
                if (response.success) {
                    this.showAlert('Eliminado', 'El sticker ha sido eliminado.', 'success')
                        .then(() => {
                            // Recarga los stickers
                            this.loadStickers();
                        });
                } else {
                    this.showAlert('Error', 'Hubo un problema al eliminar el sticker: ' + response.error, 'error');
                }
            },
            error: (xhr, status, error) => {
                this.showAlert('Error', 'Hubo un problema al eliminar el sticker: ' + xhr.responseText, 'error');
            }
        });
    }

    /**
     * Procesa la subida de un archivo de sticker
     * @param {Event} event - Evento de cambio del input file
     */
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validar el archivo
        if (!this.validateFile(file)) {
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', file.name.split('.')[0]);
        formData.append('file_name', file.name);
        formData.append('mime_type', file.type);
        
        this.uploadSticker(formData);
        
        // Limpiar el input para permitir subir el mismo archivo de nuevo
        event.target.value = '';
    }

    /**
     * Valida que el archivo sea del tipo correcto
     * @param {File} file - Archivo a validar
     * @returns {boolean} - True si el archivo es válido
     */
    validateFile(file) {
        // Verificar tipo de archivo
        if (file.type !== 'image/webp') {
            this.showAlert('Error', 'Solo se permiten archivos WebP', 'error');
            return false;
        }
        
        // Verificar tamaño (máximo 2MB)
        const maxSize = 2 * 1024 * 1024; // 2MB
        if (file.size > maxSize) {
            this.showAlert('Error', 'El archivo es demasiado grande. Máximo 2MB', 'error');
            return false;
        }
        
        return true;
    }

    /**
     * Sube un nuevo sticker al servidor
     * @param {FormData} formData - Datos del formulario
     */
    uploadSticker(formData) {
        fetch('/api/sticker/create', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                this.showAlert('Error', data.error, 'error');
            } else {
                this.showAlert('Éxito', 'Sticker creado exitosamente', 'success')
                    .then(() => {
                        this.loadStickers();
                    });
            }
        })
        .catch(error => {
            this.showAlert('Error', `Error al crear el sticker: ${error.message}`, 'error');
        });
    }

    /**
     * Envía un sticker a un chat
     * @param {string|number} chatId - ID del chat
     * @param {string} stickerUrl - URL del sticker
     * @param {string} fileName - Nombre del archivo
     */
    sendSticker(chatId, stickerUrl, fileName) {
        $.ajax({
            url: '/api/message/send-sticker',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                chat_id: chatId,
                sticker_url: stickerUrl,
                file_name: fileName
            }),
            success: (data) => {
                if (data.status === 'success') {
                    if (typeof window.loadMessages === 'function') {
                        window.loadMessages(chatId);
                    }
                } else {
                    console.error('Error sending sticker:', data.error || 'Unknown error');
                }
            },
            error: (xhr, status, error) => {
                console.error('Error sending sticker:', error);
            }
        });
    }

    /**
     * Muestra una alerta con SweetAlert2
     * @param {string} title - Título de la alerta
     * @param {string} text - Texto de la alerta
     * @param {string} icon - Icono de la alerta (success, error, warning, info, question)
     * @returns {Promise} - Promesa de SweetAlert2
     */
    showAlert(title, text, icon) {
        return Swal.fire({
            title: title,
            text: text,
            icon: icon,
            confirmButtonText: 'Cerrar'
        });
    }
}
