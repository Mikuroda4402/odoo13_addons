# -*- coding: utf-8 -*-

{
    'name': 'Sale Require',
    'summary': 'Sale Require',
    'category': 'sale',
    'version': '13.0.0',
    'author': 'Jason Wu & Monica',
    'description':
        """
        Sale Require
        """,
    'depends': ['base'],
    'auto_install': False,
    'data': [
        'security/sale_require_groups.xml',
        'security/ir.model.access.csv',
        'views/sale_require_view.xml',
        'views/require_category.xml',
        # 'views/res_partner.xml',
    ],
}