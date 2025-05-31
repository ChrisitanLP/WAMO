class NavigationModule {
    constructor() {
        this.buttons = {
            contacts: document.getElementById('contacts-btn'),
            products: document.getElementById('products-btn'),
            messages: document.getElementById('messages-btn'),
            status: document.getElementById('status-btn')
        };
        this.initialize();
    }

    initialize() {
        for (const [key, button] of Object.entries(this.buttons)) {
            if (!button) {
                console.warn(`No se encontró el botón de ${key}`);
                continue;
            }
            button.addEventListener('click', () => {
                const templateId = this.getTemplateIdFromButton(key);
                new TemplateModule().showTemplate(templateId);
                this.setActiveButton(`${key}-btn`);
            });
        }
    }

    getTemplateIdFromButton(buttonKey) {
        const templateMap = {
            'contacts': 'contacts_template',
            'products': 'products_template',
            'messages': 'default_messages_template',
            'status': 'status_template'
        };
        return templateMap[buttonKey] || 'contacts_template';
    }

    setActiveButton(activeId) {
        document.querySelectorAll('.nav-icons button').forEach(button => {
            button.classList.toggle('active', button.id === activeId);
        });
    }
}

