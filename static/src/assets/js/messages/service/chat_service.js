class ChatService {
    static updateChatStatus(chatId, status) {
        const csrfToken = $('meta[name="csrf-token"]').attr('content');
        
        return $.ajax({
            url: '/api/chat/update_status',
            type: 'POST',
            headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
            },
            data: JSON.stringify({
            chat_id: chatId,
            status_chat: status
            })
        });
    }
}