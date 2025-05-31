class ResponsiveModule {
    constructor() {
        this.mobileMediaQuery = window.matchMedia('(max-width: 768px)');
        this.tabletMediaQuery = window.matchMedia('(min-width: 769px) and (max-width: 1280px)');
    }

    initializeResponsiveness() {
        this.mobileMediaQuery.addListener(() => this.handleViewChanges());
        this.tabletMediaQuery.addListener(() => this.handleViewChanges());
        this.handleViewChanges();
    }

    handleViewChanges() {
        const container = $('.chats-and-contacts-container');
        container.removeClass('mobile-view tablet-view');

        if (this.mobileMediaQuery.matches) {
            this.setupMobileView(container);
        } else if (this.tabletMediaQuery.matches) {
            this.setupTabletView(container);
        } else {
            this.setupDesktopView(container);
        }
    }

    setupMobileView(container) {
        container.addClass('mobile-view');
        this.setupNavigationHandlers();
    }

    setupTabletView(container) {
        container.addClass('tablet-view');
        this.setupNavigationHandlers();
    }

    setupDesktopView(container) {}

    setupNavigationHandlers() {
        $(document).off('click', '.nav-btn, .close-btn-section, .interactive-item');
        $(document).on('click', '#contacts-btn', () => this.changeView('contacts-selected'));
        $(document).on('click', '#products-btn', () => this.changeView('products-selected'));
        $(document).on('click', '#messages-btn', () => this.changeView('default-messages-selected'));
        $(document).on('click', '#status-btn', () => this.changeView('status-selected'));
        $(document).on('click', '.close-btn-section', () => this.changeView('chat-selected'));
        $(document).on('click', '.chat-item, .product-item, .profile-pic, .send-icon', () => this.changeView('chat-selected'));
    }

    changeView(viewClass) {
        $('.chats-and-contacts-container').removeClass('chat-selected contacts-selected products-selected status-selected default-messages-selected').addClass(viewClass);
    }
}

