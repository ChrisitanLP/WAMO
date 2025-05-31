document.addEventListener('DOMContentLoaded', function() {
    // Remover header y footer si existen
    document.querySelector('header')?.remove();
    document.querySelector('footer')?.remove();

    // Inicializar módulos
    const navigationModule = new NavigationModule();
    const templateModule = new TemplateModule();
    const responsiveModule = new ResponsiveModule();

    // Configuración inicial
    templateModule.showTemplate('contacts_template');
    navigationModule.setActiveButton('contacts-btn');
    responsiveModule.initializeResponsiveness();
});