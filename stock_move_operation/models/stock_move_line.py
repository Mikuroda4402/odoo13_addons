# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    
    def split_quantities(self):
        for operation in self:
            if float_compare(operation.product_uom_qty, operation.qty_done, precision_rounding=operation.product_uom_id.rounding) == 1:
                operation.copy(default={'lot_id':operation.lot_id.id, 'qty_done': operation.product_uom_qty - operation.qty_done, 'product_uom_qty': operation.product_uom_qty - operation.qty_done})
                operation.write({'product_uom_qty': operation.qty_done})
            else:
                raise UserError(_('The quantity to split should be smaller than the quantity To Do.  '))
        return True

    
    def multi_split_quantities(self):
        for operation in self:
            count = round(operation.product_uom_qty / operation.qty_done) - 1
            while count > 0:
                # if float_compare(operation.product_uom_qty, operation.qty_done, precision_rounding=operation.product_uom_id.rounding) == 1:
                if operation.tracking != 'none' and operation.picking_id.picking_type_id.use_create_lots:
                    lot_id = operation.env['stock.production.lot'].create({
                        'product_id': operation.product_id.id,
                    })
                operation.copy(default={'lot_id': lot_id.id,
                                        'lot_name': lot_id.display_name,
                                        'qty_done': operation.qty_done,
                                        'product_uom_qty': operation.qty_done})
                operation.write({'product_uom_qty': operation.qty_done})
                count = count-1
        return True



