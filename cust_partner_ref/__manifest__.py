# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

{
    'name': '合作伙伴自動編號',
    'summary': '自動編號',
    'category': 'partner',
    'version': '13.0.1',
    'description':
        """
...
========================

This module provides the core of the Odoo Web Client.
        """,
    'depends': ['base'],
    'auto_install': False,
    'data': [
        'views/res_partner.xml',
        # 'data/sequence.xml'
    ],
}