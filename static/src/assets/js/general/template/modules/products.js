class ProductsModule {
    initialize() {
        this.initializeSearch();
    }

    initializeSearch() {
        const searchInput = $('#search-input-products');
        searchInput.on('input', this.debounce(this.performSearch, 300));
    }

    performSearch() {
        const query = $(this).val();
        $.ajax({
            url: '/api/products/search',
            method: 'POST',
            data: { query },
            dataType: 'json',
            success: this.handleSearchSuccess,
            error: (error) => console.error('Error en búsqueda de productos:', error)
        });
    }

    handleSearchSuccess(result) {
        if (result.status !== 'success') {
            console.error('Error:', result.message);
            return;
        }
        this.renderProducts(result.products);
    }

    renderProducts(products) {
        const productsGrid = $('.products-grid');
        productsGrid.empty();
        products.forEach(product => {
            const productItem = this.createProductItemHTML(product);
            productsGrid.append(productItem);
        });
    }

    createProductItemHTML(product) {
        return `
            <div class="product-item" data-product-id="${product.id}">
                <div class="color-line"></div>
                <div class="product-pic">
                    <img src="/web/image/product.template/${product.id}/image_1920" alt="Product Image"/>
                </div>
                <div class="product-info">
                    <div class="product-name">${product.name}</div>
                    <div class="product-price">${product.list_price} €</div>
                </div>
            </div>`;
    }

    debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
}
