# -*- coding: utf-8 -*-
{
    'name': '表單管理系統-工作聯繫單',
    'summary': '工作聯繫單/業務聯繫單',
    'version': '0.0.1',
    'category': 'Uncategory',
    'author': 'Ching Chang',
    'depends': [
        'base', 'web', 'hr', 'sequence_customize'
    ],
    'data': [
        'views/sub_work_contact_view.xml',
        'views/work_contact_view.xml',
        'views/actions.xml',
        'views/menuitem.xml',
        'views/ir_sequence_customize.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': [],
    'images': ['static/description/icon.png'],
    'application': False,
    'auto_install': False,
}