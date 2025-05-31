class LinkConverter {
    /**
     * Convert URLs in text to hyperlinks
     * @param {string} text - Text that may contain URLs
     * @returns {string} Text with URLs converted to hyperlinks
     */
    convertToLink(text) {
        if (!text) return '';
        
        const urlPattern = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
        return text.replace(urlPattern, (url) => {
            return `<a href="${url}" target="_blank">${url}</a>`;
        });
    }
}