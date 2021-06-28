# _*_ coding: utf-8 _*_
{
    'name': "purchase import",
    'description': """
        採購資料匯入模組
        Update to odoo13 version by mikuroda4402 on 2021-06-28
    """,
    'version': '1.1',
    'depends': ["stock"],
    'author': "Monica",
    'category': '',
    'description': """
        stock import picking
    """,
    'data': [
        "wizard/stock_import_picking.xml",
    ],
    'demo': [],
}
