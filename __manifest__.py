# -*- coding: utf-8 -*-
{
    'name': "Mini Clinic",

    'summary': "Medical Center Management System",

    'description': """
        Medical Center Management System
    """,

    'author': "Imran Chowdhury",
    'website': "https://www.yourcompany.com",

    'category': 'education',
    'version': '0.1',

    'depends': ['base','hr','product','sale_management','account','mail','contacts','web','portal','website','website_sale'],

    'data': [
        ## Data
        "data/sequence.xml",
        "data/email_template_data.xml",
        "data/product_product_data.xml",
        
        ## Security
        # "security/security.xml",
        "security/ir.model.access.csv",
        
        ## report
        'reports/report_action.xml',
        'reports/report_prescription_order.xml',
        
        ## Views
        "views/prescription_configuration.xml",
        "views/prescription.xml",
        "views/disease.xml",
        "views/product_view.xml",   
        "views/dashboard.xml",
        "views/appointment.xml",
        "views/prescription_template.xml",
        # "views/portal_templates.xml",
        # "views/appointment_request_form.xml",
        "views/portal_menu.xml",
        "views/appointment_slot.xml",
        "views/appointment_schedules.xml",
        
        
        ## Wizards
        
        ## Inherited Views 
        "views/res_partner_inherit.xml",
        "views/res_config_settings_views.xml",
        
        
        ## Menus
        "views/menus.xml",
        
        
    ],
    'assets': {
        'web.assets_frontend': [
            '/mini_clinic/static/src/js/portal.js',
        ], 
        'web.assets_backend': [
            '/mini_clinic/static/src/css/dashboard.scss',
        ], 
        
    },
    
    'demo': [
        # 'demo/demo.xml',
    ],
    'icon_image': '/mini_clinic/static/description/icon.png',
    'installable': True,
    'auto_install': False,
    'application': True,
    'contributors': [
        "Imran Chowdhury",
    ],
    
}

