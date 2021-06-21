# -*- coding: utf-8 -*-

from odoo import models, fields


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    subcontract = fields.Boolean('委外', default=False, help="委外工艺")
    service_product_id = fields.Many2one('product.product', '委外服务', domain=[('type', '=', 'service')])
    default_supplier = fields.Many2one('res.partner', '默认供应商', domain=[('supplier_rank', '>', 0)])
