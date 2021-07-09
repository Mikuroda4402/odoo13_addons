# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    second_unit_qty = fields.Float('Second unit qty', compute='_compute_second_qty', store=True)
    second_unit = fields.Many2one('uom.uom', 'Second unit')
    description = fields.Char('description')
    second_ratio = fields.Float('Second ratio')

    
    @api.depends('product_qty', 'second_ratio')
    def _compute_second_qty(self):
        for lot in self:
            if lot.second_ratio > 0.0:
                lot.second_unit_qty = lot.product_qty / lot.second_ratio
            else:
                lot.second_unit_qty = 0.0
