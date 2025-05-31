document.addEventListener('DOMContentLoaded', function() {
    const pickerManager = new PickerManager();
    pickerManager.init();
    
    // Exponer la instancia para depuración y posible uso externo
    window.pickerManager = pickerManager;
});

const emojiConfig = {
    categories: [
        { 
            name: 'Emoticonos', 
            icons: ['😊', '😂', '😍', '😒', '😘', '😎', '😡', '😍', '😗', '😜', '🤔', '😎', '😜', '🤗', '😄', '😆', '😅', '😩', '😢', '😲', '😰', '🥺', '😠', '😮', '😪', '😫', '😴', '😍', '😘', '😚', '😙', '🥳', '🤩', '😇', '🤔', '🙄', '😒', '🥺', '😭', '😈', '👿', '🙃', '🤯', '😤', '😣', '🤤', '🤪', '🤗', '😜', '😝', '😛', '😎', '🤑', '😲', '😳', '😱', '😨', '😰', '😢', '😥', '😓', '🤧', '🤯', '😵', '🤠', '😡', '😠', '😤', '😩', '😫', '😤', '😮', '😯', '😲']
        },
        { 
            name: 'Actividades', 
            icons: ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🥅', '🏒', '🏑', '🏏', '🥎', '🎣', '🤿', '🎽', '🏆', '🏅', '🥇', '🥈', '🥉', '🎯', '🎳', '🎮', '🕹', '🎲', '♟', '🎯', '🎳', '🎩', '🎪', '🎭', '🃏', '🎴', '🀄', '🕹', '🎲', '🎰', '🧠', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🎺', '🎷', '🎸', '🎻', '🎵', '🎶', '🎼']
        },
        { 
            name: 'Alimentos y bebidas', 
            icons: ['🍎', '🍏', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒', '🍑', '🍍', '🥭', '🥥', '🥝', '🍅', '🍆', '🥑', '🥒', '🥬', '🥦', '🥕', '🧄', '🧅', '🍠', '🥔', '🍯', '🥛', '🧃', '🧉', '🥤', '🍵', '☕', '🍶', '🍺', '🍻', '🥂', '🍷', '🥃', '🍸', '🍹', '🍾', '🥡', '🥢', '🍽', '🍴', '🥄', '🍳', '🥘', '🥗', '🍲', '🍜', '🍝', '🍞', '🥐', '🥯', '🍔', '🍟', '🍕', '🌭', '🍿', '🍩', '🍪', '🎂', '🍰', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯', '🍰', '🧁']
        },
        { 
            name: 'Personas', 
            icons: ['👶', '👧', '👦', '👩', '👨', '👴', '👵', '👶', '👸', '👳', '👲', '🧕', '🤴', '👸', '👷', '👮', '👯', '👼', '🤰', '🤱', '👩‍🔬', '👩‍🏫', '👩‍⚕️', '👩‍🍳', '👩‍🎓', '👩‍🚒', '👩‍✈️', '👩‍🚀', '👩‍⚖️', '🧑‍🧑', '👩‍🧑', '🧑‍🤝‍🧑', '👬', '👭', '👩‍❤️‍👩', '👩‍❤️‍👨', '👨‍❤️‍👨', '👨‍❤️‍👩', '👩‍❤️‍👩', '👨‍❤️‍👩', '👩‍❤️‍👨', '👨‍❤️‍👨']
        },
        { 
            name: 'Animales', 
            icons: ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🦁', '🐯', '🐨', '🦝', '🦋', '🐞', '🐜', '🦗', '🕷️', '🕸️', '🦂', '🐍', '🦎', '🐢', '🐸', '🦉', '🦅', '🦜', '🦚', '🦆', '🦑', '🐙','🦞', '🦈', '🐠', '🐟', '🐡', '🦕', '🦖', '🐬', '🐳', '🐋', '🦑', '🦚', '🦜', '🦇', '🦦', '🦈', '🦟', '🦠', '🦐', '🦋', '🦄', '🐉']
        },
        { 
            name: 'Viajes y lugares', 
            icons: ['🌍', '🌎', '🌏', '🏔️', '⛰️', '🗻', '🌋', '🏜️', '🏝️', '🏖️', '🏕️', '🏠', '🏡', '🏘️', '🏚️', '🏛️', '🏟️', '🏗️', '🏘️', '🏚️', '🕌', '🕍', '🕋', '⛪', '🛕', '🏰', '🏯', '🏬', '🏢', '🏣', '🏤', '🏥', '🏦', '🏪', '🏫', '🏩', '🏨']
        },
        { 
            name: 'Objetos', 
            icons: ['📱', '📲', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '🖲️', '💽', '💾', '💿', '📀', '📼', '📹', '📺', '📷', '📸', '📽', '🎥', '📞', '☎️', '📟', '📠', '📧', '📨', '📩', '📪', '📫', '📬', '📭', '📮', '📯', '📥', '📤']
        },
        { 
            name: 'Simbolos', 
            icons: ['❤️', '💔', '💖', '💗', '💙', '💚', '💛', '💜', '🖤', '🤍', '🤎', '💝', '💞', '💟', '❣️', '💕', '💓', '💔', '🧡', '💯']
        }
    ]
};

class PickerManager {
    constructor() {
        this.elements = {
            emojiBtn: document.getElementById('emoji-btn'),
            closeEmojiPickerBtn: document.getElementById('close-emoji-picker'),
            emojiPicker: document.getElementById('emoji-picker'),
            emojiPickerBody: document.querySelector('.emoji-picker-body'),
            messageInput: document.getElementById('message-input'),
            stickerPicker: document.getElementById('sticker-picker'),
            plusPicker: document.getElementById('plus-picker'),
            plusBtn: document.getElementById('plus-btn')
        };
        
        this.currentOpenPicker = null;
        this.initialized = false;
    }

    /**
     * Inicializa todos los componentes del selector
     */
    init() {
        if (this.initialized) return;
        
        this.setupEventListeners();
        this.renderEmojiPicker();
        
        this.initialized = true;
        console.log('Picker Manager inicializado correctamente');
    }

    /**
     * Configura todos los event listeners necesarios
     */
    setupEventListeners() {
        // Event listener para cerrar los pickers al hacer clic fuera
        document.addEventListener('click', this.handleOutsideClick.bind(this));
        
        // Configurar botones si existen
        if (this.elements.emojiBtn) {
            this.elements.emojiBtn.addEventListener('click', this.toggleEmojiPicker.bind(this));
        }
        
        if (this.elements.closeEmojiPickerBtn) {
            this.elements.closeEmojiPickerBtn.addEventListener('click', () => this.closePicker('emojiPicker'));
        }
        
        if (this.elements.plusBtn) {
            this.elements.plusBtn.addEventListener('click', this.togglePlusPicker.bind(this));
        }
    }

    /**
     * Maneja clics fuera de los pickers para cerrarlos
     * @param {Event} e - Evento de clic
     */
    handleOutsideClick(e) {
        const { emojiPicker, emojiBtn, plusPicker, plusBtn, stickerPicker } = this.elements;
        
        // Cerrar emoji picker si está abierto y se hace clic fuera
        if (emojiPicker && emojiPicker.style.display === 'block' && 
            !e.target.closest('#emoji-picker, #emoji-btn')) {
            this.closePicker('emojiPicker');
        }
        
        // Cerrar plus picker si está abierto y se hace clic fuera
        if (plusPicker && plusPicker.style.display === 'block' && 
            !e.target.closest('#plus-picker, #plus-btn')) {
            this.closePicker('plusPicker');
        }
        
        // Cerrar sticker picker si está abierto y se hace clic fuera
        if (stickerPicker && stickerPicker.style.display === 'block' && 
            !e.target.closest('#sticker-picker, .sticker-trigger')) {
            this.closePicker('stickerPicker');
        }
    }

    /**
     * Cierra todos los pickers abiertos
     */
    closeAllPickers() {
        const pickerKeys = ['emojiPicker', 'stickerPicker', 'plusPicker'];
        
        pickerKeys.forEach(key => {
            if (this.elements[key]) {
                this.elements[key].style.display = 'none';
            }
        });
        
        // Resetear el botón plus a su estado original
        if (this.elements.plusBtn) {
            this.elements.plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
        }
        
        this.currentOpenPicker = null;
    }

    /**
     * Cierra un picker específico
     * @param {string} pickerKey - Clave del picker a cerrar
     */
    closePicker(pickerKey) {
        if (this.elements[pickerKey]) {
            this.elements[pickerKey].style.display = 'none';
            
            if (pickerKey === 'plusPicker' && this.elements.plusBtn) {
                this.elements.plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
            }
            
            if (this.currentOpenPicker === pickerKey) {
                this.currentOpenPicker = null;
            }
        }
    }

    /**
     * Alterna la visibilidad del selector de emojis
     */
    toggleEmojiPicker() {
        const { emojiPicker } = this.elements;
        
        if (!emojiPicker) return;
        
        const isHidden = emojiPicker.style.display === 'none' || emojiPicker.style.display === '';
        
        if (isHidden) {
            this.closeAllPickers();
            emojiPicker.style.display = 'block';
            this.currentOpenPicker = 'emojiPicker';
        } else {
            emojiPicker.style.display = 'none';
            this.currentOpenPicker = null;
        }
    }

    /**
     * Alterna la visibilidad del selector plus
     */
    togglePlusPicker() {
        const { plusPicker, plusBtn } = this.elements;
        
        if (!plusPicker || !plusBtn) return;
        
        const isHidden = plusPicker.style.display === 'none' || plusPicker.style.display === '';
        
        if (isHidden) {
            this.closeAllPickers();
            plusPicker.style.display = 'block';
            plusBtn.innerHTML = '<i class="fa fa-times message-icon" aria-hidden="true"></i>';
            this.currentOpenPicker = 'plusPicker';
        } else {
            plusPicker.style.display = 'none';
            plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
            this.currentOpenPicker = null;
        }
    }

    /**
     * Renderiza las categorías y emojis en el selector
     */
    renderEmojiPicker() {
        const { emojiPickerBody, messageInput } = this.elements;
        
        if (!emojiPickerBody || !messageInput) return;
        
        // Limpiar el contenido existente
        emojiPickerBody.innerHTML = '';
        
        // Crear fragmento para optimizar el rendimiento
        const fragment = document.createDocumentFragment();
        
        // Renderizar cada categoría
        emojiConfig.categories.forEach(category => {
            const sectionDiv = this.createCategorySection(category, messageInput);
            fragment.appendChild(sectionDiv);
        });
        
        // Añadir todo el contenido de una vez para reducir reflow
        emojiPickerBody.appendChild(fragment);
    }

    /**
     * Crea una sección de categoría con sus emojis
     * @param {Object} category - Datos de la categoría
     * @param {HTMLElement} messageInput - Elemento de entrada de mensaje
     * @returns {HTMLElement} - Elemento div de la sección
     */
    createCategorySection(category, messageInput) {
        const sectionDiv = document.createElement('div');
        sectionDiv.classList.add('emoji-section');
        
        // Crear encabezado
        const sectionHeader = document.createElement('h3');
        sectionHeader.textContent = category.name;
        sectionDiv.appendChild(sectionHeader);
        
        // Crear contenedor para los emojis (para optimizar el layout)
        const emojiContainer = document.createElement('div');
        emojiContainer.classList.add('emoji-container');
        
        // Creamos fragmento para optimizar rendimiento
        const fragment = document.createDocumentFragment();
        
        // Añadir emojis
        category.icons.forEach(emoji => {
            const emojiSpan = document.createElement('span');
            emojiSpan.classList.add('emoji');
            emojiSpan.textContent = emoji;
            
            // Usar delegación de eventos para mejorar rendimiento
            emojiSpan.dataset.emoji = emoji;
            
            fragment.appendChild(emojiSpan);
        });
        
        emojiContainer.appendChild(fragment);
        sectionDiv.appendChild(emojiContainer);
        
        // Añadir un único event listener para todos los emojis de esta sección
        emojiContainer.addEventListener('click', (e) => {
            const target = e.target;
            
            if (target.classList.contains('emoji')) {
                // Insertamos el emoji en la posición actual del cursor
                this.insertEmojiAtCursor(messageInput, target.dataset.emoji);
                this.closePicker('emojiPicker');
            }
        });
        
        return sectionDiv;
    }

    /**
     * Inserta un emoji en la posición actual del cursor
     * @param {HTMLElement} inputElement - Elemento de entrada de texto
     * @param {string} emoji - Emoji a insertar
     */
    insertEmojiAtCursor(inputElement, emoji) {
        if (!inputElement || !emoji) return;
        
        // Guardar posición del cursor
        const startPos = inputElement.selectionStart;
        const endPos = inputElement.selectionEnd;
        
        // Texto antes y después del cursor
        const beforeText = inputElement.value.substring(0, startPos);
        const afterText = inputElement.value.substring(endPos);
        
        // Insertar emoji
        inputElement.value = beforeText + emoji + afterText;
        
        // Restaurar posición del cursor después del emoji
        const newCursorPos = startPos + emoji.length;
        inputElement.setSelectionRange(newCursorPos, newCursorPos);
        
        // Enfocar el input
        inputElement.focus();
        
        // Disparar evento de cambio para notificar a otros componentes
        const event = new Event('input', { bubbles: true });
        inputElement.dispatchEvent(event);
    }
}
