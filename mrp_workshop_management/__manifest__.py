# -*- encoding: utf-8 -*-

{
    "name": "Mrp Workshop Management",
    "version": "13.0.0.0.1",
    "author": "OSSTW JasonWu(jaronemo@msn.com)",
    "category": "Manufacturing",
    "website": "",
    "depends": [
        'mrp', 'stock_move_operation',
    ],
    "data": [
        'views/mrp_production_view.xml',
        'views/mrp_workorder_view.xml',
        'views/mrp_workcenter_view.xml',
        'views/mrp_routing_workcenter_view.xml',
        'views/mrp_workcenter_productivity_view.xml'
    ],
    'installable': True
}
