# -*- coding: utf-8 -*-
{
    'name': "MessageApp",
    'description': 'El módulo de integración de Odoo con WhatsApp, utilizando la API de whatsapp-web.js, permite enviar y recibir mensajes de WhatsApp directamente desde Odoo, sincronizar contactos, configurar plantillas de mensajes predefinidos, enviar información de productos, automatizar mensajes en eventos específicos y guardar el historial de conversaciones, mejorando así la comunicación con los clientes y optimizando los procesos de negocio.',
    'author': "CodeCraft Studios",
    'website': "https://chrisitanlp.github.io/",
    'support': 'https://chrisitanlp.github.io/',

    'price': 0.0,
    'currency': 'USD',
    'category': 'Discuss/Sales/CRM',
    'version': '16.0.1',
    'application': True,
    'installable': True,
    'license': 'OPL-1',

    'depends': [
        'base',
        'sales_team',
        'product',
        'website',
    ],

    'icon': '/message_app/static/description/icon.png',

    'data': [
        'security/ir.model.access.csv',

        'data/ir_config_parameter_data.xml',
        'data/ir_cron.xml',

        'views/base_templates.xml',

        'views/connection/authentication_base.xml',
        'views/connection/components/connection_modal.xml',
        'views/connection/components/connection_table.xml',
        'views/connection/components/qr_modal.xml',
        'views/connection/components/connection_list.xml',
        'views/connection/components/script.xml',

        'views/landing/menu_item.xml',
        'views/landing/menu_option.xml',
        'views/landing/components/connect_section.xml',
        'views/landing/components/explore_section.xml',
        'views/landing/components/script.xml',

        'views/error/error_base.xml',
        'views/error/error_template.xml',

        'views/aplication/products/products_base.xml',
        'views/aplication/products/components/products_search.xml',
        'views/aplication/products/components/products_pagination.xml',
        'views/aplication/products/components/products_header.xml',
        'views/aplication/products/components/products_grid.xml',
        'views/aplication/products/components/product_card.xml',

        'views/aplication/default_message/default_message_base.xml',
        'views/aplication/default_message/components/messages_grid.xml',
        'views/aplication/default_message/components/message_modal.xml',
        'views/aplication/default_message/components/message_content.xml',
        'views/aplication/default_message/components/individual_message_item.xml',
        'views/aplication/default_message/components/header.xml',
        'views/aplication/default_message/components/add_message.xml',

        'views/aplication/contacts/contacts_base.xml',
        'views/aplication/contacts/components/contact_search.xml',
        'views/aplication/contacts/components/contact_modal.xml',
        'views/aplication/contacts/components/contact_item.xml',
        'views/aplication/contacts/components/contact_header.xml',
        'views/aplication/contacts/components/contact_grid.xml',
        'views/aplication/contacts/components/contact_card.xml',
        'views/aplication/contacts/components/contact_add_button.xml',

        'views/aplication/base/base_base.xml',
        'views/aplication/base/components/base_header.xml',
        'views/aplication/base/components/base_scripts.xml',
        'views/aplication/base/scripts/scripts_aplication.xml',
        'views/aplication/base/scripts/scripts_general.xml',
        'views/aplication/base/scripts/scripts_mssage.xml',
        'views/aplication/base/scripts/scripts_basic.xml',

        'views/aplication/chats/chats_base.xml',
        'views/aplication/chats/components/chat_list_section.xml',
        'views/aplication/chats/components/chat_message_preview.xml',
        'views/aplication/chats/components/chat_message_type.xml',
        'views/aplication/chats/components/chat_profile.xml',

        'views/aplication/messages/messages_base.xml',
        'views/aplication/messages/components/message_attend_button.xml',
        'views/aplication/messages/components/message_edit.xml',
        'views/aplication/messages/components/message_file_preview.xml',
        'views/aplication/messages/components/message_input.xml',
        'views/aplication/messages/components/message_input_disabled.xml',
        'views/aplication/messages/components/message_navigate.xml',
        'views/aplication/messages/components/message_pickers.xml',
        'views/aplication/messages/components/message_reply.xml',
        'views/aplication/messages/components/message_viewers.xml',
    ],

    'assets':{
        'web.assets_backend': [
            'message_app/static/src/assets/js/qrcode.min.js',
            'message_app/static/src/assets/js/connection/**/*.js',
            #'message_app/static/src/assets/js/general/**/**/*.js',
            #'message_app/static/src/assets/js/messages/**/*.js',
            #'message_app/static/src/assets/js/aplication/**/*.js',
        ],
        'web.assets_frontend': [
            'message_app/static/src/assets/js/qrcode.min.js',
            'message_app/static/src/styles/scss/landing.scss',
            'message_app/static/src/styles/scss/connection.scss',
            'message_app/static/src/styles/scss/error.scss',
            'message_app/static/src/assets/js/sweetalert2.min.js',
            'message_app/static/src/styles/basic/custom_style.scss',
            #'message_app/static/src/styles/scss/base.scss',
            #'message_app/static/src/styles/scss/chats.scss',
        ],
    }
}

