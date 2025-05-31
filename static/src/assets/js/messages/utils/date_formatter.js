class DateFormatter {
    /**
     * Get display date string and update last date tracker
     * @param {string} timestamp - ISO timestamp 
     * @param {string} lastDisplayedDate - Last displayed date for comparison
     * @returns {Object} Object containing displayDate and updated lastDate
     */
    getDisplayDate(timestamp, lastDisplayedDate) {
        const originalDate = new Date(timestamp);
        originalDate.setHours(originalDate.getHours() - 5); // Adjust for timezone
        
        const currentDate = new Date();
        let displayDate = '';
        
        if (this.isSameDay(originalDate, currentDate)) {
            displayDate = 'Hoy';
        } else if (this.isSameDay(originalDate, new Date(currentDate.setDate(currentDate.getDate() - 1)))) {
            displayDate = 'Ayer';
        } else {
            displayDate = originalDate.toLocaleDateString();
        }
        
        return { displayDate, lastDate: displayDate };
    }
    
    /**
     * Format timestamp for individual messages
     * @param {string} timestamp - ISO timestamp
     * @returns {string} Formatted time string
     */
    formatMessageTime(timestamp) {
        const originalDate = new Date(timestamp);
        originalDate.setHours(originalDate.getHours() - 5); // Adjust for timezone
        return originalDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    /**
     * Check if two dates represent the same day
     * @param {Date} date1 - First date
     * @param {Date} date2 - Second date
     * @returns {boolean} True if dates are the same day
     */
    isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }
}