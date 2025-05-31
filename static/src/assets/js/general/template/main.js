class TemplateModule {
    showTemplate(templateId) {
        $.ajax({
            url: `/api/whatsapp/${templateId}`,
            method: 'GET',
            dataType: 'html',
            success: (data) => {
                $("#dynamic-template").html(data);
                this.initializeModuleByTemplateId(templateId);
                new ResponsiveModule().handleViewChanges();
            },
            error: () => {
                $("#dynamic-template").html('<p>Error loading template</p>');
            }
        });
    }

    initializeModuleByTemplateId(templateId) {
        const moduleMap = {
            'contacts_template': ContactsModule,
            'products_template': ProductsModule,
            'default_messages_template': MessagesModule,
            'status_template': StatusModule
        };
        
        const ModuleConstructor = moduleMap[templateId];
        if (ModuleConstructor) {
            new ModuleConstructor().initialize();
        }
    }
}

