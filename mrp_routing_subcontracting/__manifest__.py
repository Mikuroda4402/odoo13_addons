# -*- encoding: utf-8 -*-

{
    "name": "MRP Subcontracting",
    "version": "12.0.0.0.1",
    "author": "宁波鼎航信息技术有限公司",
    "category": "Manufacturing",
    "website": "http://www.odooshz.xyz",
    "depends": [
        'purchase',
        'mrp'
    ],
    "data": [
        'wizard/mrp_workorder_subcontract_wizard_view.xml',
        'views/mrp_routing_workcenter_view.xml',
        'views/mrp_workorder_view.xml',
        "security/ir.model.access.csv",

    ],
    'installable': True
}
