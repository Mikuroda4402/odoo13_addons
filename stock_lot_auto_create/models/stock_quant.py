# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    second_unit_qty = fields.Float('Second unit qty', compute='_compute_second_qty', store=True)
    second_unit = fields.Many2one('uom.uom', related='lot_id.second_unit', string='Second unit', store=True)
    description = fields.Char('description', related='lot_id.description', store=True)
    second_ratio = fields.Float('Second ratio', related='lot_id.second_ratio', store=True)

    
    @api.depends('quantity', 'second_ratio')
    def _compute_second_qty(self):
        for quant in self:
            if quant.second_ratio > 0.0:
                quant.second_unit_qty = quant.quantity / quant.second_ratio
            else:
                quant.second_unit_qty = 0.0
