from odoo import models, fields, api


class StockMveLine(models.Model):
    _inherit = 'stock.move.line'

    second_unit = fields.Many2one('uom.uom', 'Second unit')
    description = fields.Char('description')
    second_ratio = fields.Float('Second ratio')
    second_unit_qty = fields.Float('Second unit qty')
    ref = fields.Char('partner ref')

    @api.onchange('qty_done')
    def onchange_qty(self):
        if self.tracking != 'none' and self.picking_id.picking_type_id.use_create_lots:
            if not self.lot_id and self.qty_done > 0:
                lot_id = self.env['stock.production.lot'].create({'product_id': self.product_id.id})
                self.lot_id = lot_id
                self.lot_name = self.lot_id.display_name

    @api.onchange('second_ratio', 'second_unit_qty')
    def onchange_second_unit(self):
        if self.second_unit_qty > 0 and self.second_ratio > 0:
            self.qty_done = self.second_unit_qty * self.second_ratio

    
    def write(self, vals):
        res = super(StockMveLine, self).write(vals)
        for line in self:
            if line.lot_id:
                if line.second_unit:
                    line.lot_id.second_unit = line.second_unit
                if line.description:
                    line.lot_id.description = line.description
                if line.second_ratio > 0:
                    line.lot_id.second_ratio = line.second_ratio
                if line.ref:
                    line.lot_id.ref = line.ref
        return res

    @api.model
    def create(self, vals):
        res = super(StockMveLine, self).create(vals)
        if res.lot_id:
            if res.second_unit:
                res.lot_id.second_unit = res.second_unit
            if res.description:
                res.lot_id.description = res.description
            if res.second_ratio > 0:
                res.lot_id.second_ratio = res.second_ratio
            if res.ref:
                res.lot_id.ref = res.ref
        return res


