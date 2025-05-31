class FilePreviewManager {
    static hidePreview() {
        this.togglePreview(false);
        $('#preview-image').attr('src', '').hide();
        $('#preview-video').attr('src', '').hide();
        $('#preview-document').attr('src', '').hide();
        $('#file-message').val('');
    }
  
    static togglePreview(visible) {
        if (visible) {
            $('#file-preview').addClass('visible');
        } else {
            $('#file-preview').removeClass('visible');
        }
    }
}