# -*- encoding: utf-8 -*-

{
    "name": "Mrp Workshop Trace",
    "version": "13.0.0.0.1",
    "author": "Mikuroda(mainfire41@gmail.com)",
    "category": "Manufacturing",
    "website": "mikuroda4402.github.io",
    "depends": [
        'mrp', 'stock_move_operation'
    ],
    "data": [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/mrp_production_view.xml',
    ],
    'installable': True
}
