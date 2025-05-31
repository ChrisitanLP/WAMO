class MessageRenderer {
    constructor() {
        this.dateFormatter = new DateFormatter();
        this.mediaRenderer = new MediaRenderer();
        this.linkConverter = new LinkConverter();
    }

    /**
     * Render chat banner with profile information
     * @param {Object} chat - Chat information
     * @returns {string} HTML for chat banner
     */
    renderChatBanner(chat) {
        return `
            <div class="chat-banner">
                <img class="chat-profile-pic" src="${chat.profile_pic_url || 'default-profile-pic-url'}" alt="Profile Picture">
                <span class="chat-name">${chat.name || 'Desconocido'}</span>
            </div>
        `;
    }

    /**
     * Render chat banner for error state
     * @param {Object} chatInfo - Chat information
     * @returns {string} HTML for error state chat banner
     */
    renderErrorChatBanner(chatInfo) {
        const name = chatInfo.name || 'Desconocido';
        const profilePic = chatInfo.profile_pic_url || 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg';
        
        return `
            <div class="chat-banner">
                <img class="chat-profile-pic" src="${profilePic}" alt="Profile Picture">
                <span class="chat-name">${name}</span>
            </div>
        `;
    }

    /**
     * Render all messages for a chat
     * @param {Array} messages - Array of message objects
     * @param {Object} chat - Chat information
     * @returns {string} HTML for all messages
     */
    renderMessages(messages, chat) {
        const isGroupChat = chat.is_group;
        let lastDisplayedDate = null;
        let messagesHtml = '';
        
        messages.forEach((msg, index) => {
            const { displayDate, lastDate } = this.dateFormatter.getDisplayDate(msg.timestamp, lastDisplayedDate);
            
            // Add date indicator if date changed
            if (displayDate !== lastDisplayedDate) {
                if (lastDisplayedDate !== null) {
                    messagesHtml += '</div>'; // Close previous date group
                }
                messagesHtml += `<div class="date-group">`;
                messagesHtml += `<div class="date-indicator sticky-date">${displayDate}</div>`;
                lastDisplayedDate = displayDate;
            }
            
            // Render individual message
            messagesHtml += this.renderSingleMessage(msg, index, isGroupChat, chat);
        });
        
        // Close the last date group if exists
        if (lastDisplayedDate !== null) {
            messagesHtml += '</div>';
        }
        
        return messagesHtml;
    }

    /**
     * Render a single message
     * @param {Object} msg - Message object
     * @param {number} index - Message index
     * @param {boolean} isGroupChat - Whether this is a group chat
     * @param {Object} chat - Chat information
     * @returns {string} HTML for single message
     */
    renderSingleMessage(msg, index, isGroupChat, chat) {
        const messageClass = msg.from_Me ? 'from-me' : 'from-them';
        const timestamp = this.dateFormatter.formatMessageTime(msg.timestamp);
        const messageId = `message-${index}`;
        const idMessage = msg.id;
        
        // Get sender information for group chats
        const memberInfo = this.getSenderInfo(msg, isGroupChat);
        
        // Start building message HTML
        let html = `<div id="${messageId}" class="message ${messageClass}" data-message-type="${msg.type}">`;
        
        // Add member name for group chats
        if (isGroupChat && memberInfo) {
            html += `<span class="message-member-name">${memberInfo}</span>`;
        }
        
        // Add timestamp and options button
        html += `<span class="message-timestamp">${timestamp}</span>`;
        html += `<button class="message-options-btn" data-message-id="${idMessage}" data-message-index="${messageId}" data-message-type="${msg.type}" data-is-starred="${msg.is_starred}"><i class="fa fa-chevron-down"></i></button>`;
        
        // Add forwarded and starred indicators
        html += this.renderMessageIndicators(msg);
        
        // Render message content based on type
        html += this.renderMessageContent(msg);
        
        html += '</div>';
        return html;
    }

    /**
     * Extract sender information from message
     * @param {Object} msg - Message object
     * @param {boolean} isGroupChat - Whether this is a group chat
     * @returns {string} Sender information or empty string if not applicable
     */
    getSenderInfo(msg, isGroupChat) {
        if (!isGroupChat) return '';
        
        const serializedParts = msg.serialized.split('_');
        const senderPhone = serializedParts.length > 0 ? serializedParts[serializedParts.length - 1].split('@')[0] : '';
        
        if (senderPhone) {
            const lastNineDigits = senderPhone.slice(-9);
            return '0' + lastNineDigits;
        }
        
        return '';
    }

    /**
     * Render message indicators (forwarded, starred)
     * @param {Object} msg - Message object
     * @returns {string} HTML for message indicators
     */
    renderMessageIndicators(msg) {
        let html = '';
        
        // Forwarded indicator
        if (msg.is_forwarded) {
            html += '<div class="forwarded-message-label"><i class="fa fa-share" aria-hidden="true"></i> Reenviado</div>';
        }
        
        // Starred indicator
        if (msg.is_starred) {
            html += '<div class="starred-message-icon"><i class="fa fa-star"></i></div>';
        }
        
        return html;
    }

    /**
     * Render quoted message if present
     * @param {Object} msg - Message object
     * @returns {string} HTML for quoted message
     */
    renderQuotedMessage(msg) {
        if (!msg.hasQuotedMsg) return '';
        
        const quotedMessageContent = this.getQuotedMessageContent(msg);
        
        return `
            <div class="quoted-message ${msg.from_Me ? 'from-me' : 'from-them'}">
                <span class="quoted-message-body">${quotedMessageContent}</span>
            </div>
        `;
    }

    /**
     * Get content for quoted message based on type
     * @param {Object} msg - Message object
     * @returns {string} Content for quoted message
     */
    getQuotedMessageContent(msg) {
        switch (msg.quoted_type) {
            case 'image':
                return '<i class="fa fa-image message-icon" aria-hidden="true"></i><span> Imagen</span>';
            case 'video':
                return '<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span> Video</span>';
            case 'sticker':
                return '<i class="fa fa-sticky-note message-icon"></i><span> Sticker</span>';
            case 'ptt':
            case 'audio':
                return '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span>';
            case 'groups_v4_invite':
                return '<i class="fa fa-users message-icon" aria-hidden="true"></i><span> Invitación de Grupo</span>';
            case 'document':
                return '<i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span>';
            case 'vcard':
                return '<i class="fa fa-address-card message-icon" aria-hidden="true"></i><span> Contacto</span>';
            case 'location':
                return '<i class="fa fa-map-marker message-icon" aria-hidden="true"></i><span> Ubicación</span>';
            case 'chat':
                return msg.quoted_body || 'Sin contenido';
            default:
                return 'Sin contenido';
        }
    }

    /**
     * Render message content based on type
     * @param {Object} msg - Message object
     * @returns {string} HTML for message content
     */
    renderMessageContent(msg) {
        const quotedMessageHtml = this.renderQuotedMessage(msg);
        
        let contentHtml = `<p class="message-body">${quotedMessageHtml}`;
        
        switch (msg.type) {
            case 'sticker':
                contentHtml += this.mediaRenderer.renderSticker(msg);
                break;
            case 'location':
                contentHtml += this.mediaRenderer.renderLocation(msg);
                break;
            case 'image':
                contentHtml += this.mediaRenderer.renderImage(msg);
                break;
            case 'vcard':
                contentHtml += this.mediaRenderer.renderContact(msg);
                break;
            case 'document':
                contentHtml += this.mediaRenderer.renderDocument(msg);
                break;
            case 'video':
                contentHtml += this.mediaRenderer.renderVideo(msg);
                break;
            case 'ptt':
            case 'audio':
                contentHtml += this.mediaRenderer.renderAudio(msg);
                break;
            case 'revoked':
                contentHtml += '<i class="fa fa-ban message-icon" aria-hidden="true"></i><span> Se elimino este mensaje</span>';
                break;
            default:
                contentHtml += `<span class="text-message-body">${msg.body || 'Sin contenido'}</span>`;
                break;
        }
        
        contentHtml += '</p>';
        return contentHtml;
    }
}