class MediaRenderer {
    constructor() {
        this.linkConverter = new LinkConverter();
    }

    /**
     * Render sticker content
     * @param {Object} msg - Message object
     * @returns {string} HTML for sticker
     */
    renderSticker(msg) {
        if (msg.media_data) {
            return `<img src="${msg.media_data}" alt="Sticker" class="message-media-sticker">`;
        } else {
            return '<i class="fa fa-sticky-note message-icon"></i><span> Sticker</span>';
        }
    }

    /**
     * Render location content
     * @param {Object} msg - Message object
     * @returns {string} HTML for location
     */
    renderLocation(msg) {
        if (msg.latitude) {
            const latitude = msg.latitude;
            const longitude = msg.longitude;
            const locationUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

            return `
                <div class="location-container">
                    <a href="${locationUrl}" target="_blank" class="location-link">
                        <div class="location-details">
                            <i class="fa fa-map-marker location-icon" aria-hidden="true"></i>
                            <span class="location-coordinates">Lat: ${latitude}, Long: ${longitude}</span>
                        </div>
                    </a>
                </div>
            `;
        } else {
            return '<i class="fa fa-map-marker message-icon"></i><span> Ubicación</span>';
        }
    }

    /**
     * Render image content
     * @param {Object} msg - Message object
     * @returns {string} HTML for image
     */
    renderImage(msg) {
        if (msg.media_data) {
            let html = `<img src="${msg.media_data}" alt="Image" class="message-media-img">`;
            
            if (msg.body) {
                html += `<span class="text-message-body-img">${this.linkConverter.convertToLink(msg.body)}</span>`;
            }
            
            return html;
        } else {
            return '<i class="fa fa-image message-icon" aria-hidden="true"></i><span> Imagen</span>';
        }
    }

    /**
     * Render contact card
     * @param {Object} msg - Message object
     * @returns {string} HTML for contact card
     */
    renderContact(msg) {
        const vcardData = msg.body;
        const nameMatch = vcardData.match(/FN:(.+)/);
        const contactName = nameMatch ? nameMatch[1].trim() : 'Nombre desconocido';
        
        const contactPhone = this.extractContactPhone(vcardData);
        const cleanedContactPhone = contactPhone.replace(/[\s+]/g, '');
        
        return `
            <div class="vcard-container">
                <i class="fa fa-user-circle contact-icon" aria-hidden="true"></i>
                <div class="contact-info">
                    <span class="contact-name">${contactName}</span>
                    <span class="contact-phone">${contactPhone}</span>
                    <button class="save-contact-btn" data-client-id="${window.currentChatInfo?.user_id || ''}" 
                            data-contact-phone="${cleanedContactPhone}" 
                            data-contact-name="${contactName}">Añadir Contacto</button>
                </div>
            </div>
        `;
    }

    /**
     * Extract phone number from vCard data
     * @param {string} vcardData - The vCard data string
     * @returns {string} Extracted phone number or default text
     */
    extractContactPhone(vcardData) {
        const phoneRegexes = [
            /TEL(;type=[A-Z]+)?(;waid=\d+)?:(.+)/,
            /item\d+.TEL(;waid=\d+)?:(.+)/,
            /TEL;waid=\d+:(.+)/,
            /TEL:(.+)/,
            /item\d+.TEL:(.+)/,
            /TEL;type=CELL:(.+)/,
            /item1.TEL:(.+)/
        ];
        
        for (let i = 0; i < phoneRegexes.length; i++) {
            const phoneMatch = vcardData.match(phoneRegexes[i]);
            if (phoneMatch) {
                return phoneMatch[3] ? phoneMatch[3].trim() : phoneMatch[2].trim();
            }
        }
        
        return 'Teléfono desconocido';
    }

    /**
     * Render document content
     * @param {Object} msg - Message object
     * @returns {string} HTML for document
     */
    renderDocument(msg) {
        let html = '';
        
        if (msg.media_temp_url) {
            html += `
                <a href="${msg.media_temp_url}" target="_blank" download="document">
                    <i class="fa fa-file message-icon" aria-hidden="true"></i>
                    <span> ${msg.body}</span>
                </a>
            `;
        } else {
            html += '<i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span>';
        }
        
        if (msg.body && (!msg.media_temp_url || html.indexOf(msg.body) === -1)) {
            html += `<span class="text-message-body-img">${this.linkConverter.convertToLink(msg.body)}</span>`;
        }
        
        return html;
    }

    /**
     * Render video content
     * @param {Object} msg - Message object
     * @returns {string} HTML for video
     */
    renderVideo(msg) {
        let html = '';
        
        if (msg.media_temp_url) {
            html += `
                <video controls width="90%">
                    <source src="${msg.media_temp_url}" type="${msg.media_mime_type}">
                    Your browser does not support the video tag.
                </video>
            `;
        } else {
            html += '<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span> Video</span>';
        }
        
        if (msg.body) {
            html += `<span class="text-message-body-img">${this.linkConverter.convertToLink(msg.body)}</span>`;
        }
        
        return html;
    }

    /**
     * Render audio content
     * @param {Object} msg - Message object
     * @returns {string} HTML for audio
     */
    renderAudio(msg) {
        if (msg.media_data) {
            return `
                <audio controls>
                    <source src="${msg.media_data}" type="${msg.media_mime_type}">
                    Your browser does not support the audio element.
                </audio>
            `;
        } else {
            return '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span>';
        }
    }
}