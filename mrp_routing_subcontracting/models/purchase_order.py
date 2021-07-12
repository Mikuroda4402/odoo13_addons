# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    workorder_id = fields.Many2one(
        'mrp.workorder', '工单')
    production_id = fields.Many2one(
        'mrp.production', string='生产单', store=True,
        related="workorder_id.production_id")

    
    @api.depends('order_id.name', 'product_id.display_name', 'name')
    def name_get(self):
        result = []
        for po_line in self:
            name = po_line.order_id.name
            if po_line.product_id:
                name += ':' + po_line.product_id.display_name + '   ' + po_line.name
            result.append((po_line.id, name))
        return result

