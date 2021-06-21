# _*_ coding: utf-8 _*_
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MrpWorkorderSubcontractWizard(models.TransientModel):
    _name = 'mrp.workorder.subcontract.wizard'

    supplier = fields.Many2one('res.partner', '供应商', domain=[('supplier', '=', True)])
    workorder_id = fields.Many2one('mrp.workorder', '工单')
    qty_subcontract = fields.Float('委外数量')

    @api.model
    def default_get(self, fields):
        res = super(MrpWorkorderSubcontractWizard, self).default_get(fields)
        if self.env.context['active_model'] == 'mrp.workorder':
            workorder = self.env['mrp.workorder'].browse(self.env.context['active_id'])
            if workorder.subcontract_qty:
                if workorder.qty_produced > workorder.subcontract_qty:
                    qty = workorder.qty_remaining
                else:
                    qty = workorder.qty_production - workorder.subcontract_qty
            else:
                qty = workorder.qty_remaining
            if qty <= 0:
                raise UserError('不能超工单数委外')
            res.update({'workorder_id': workorder.id,
                        'supplier': workorder.supplier.id,
                        'qty_subcontract': qty
                        })
        return res

    
    def purchase_order_create(self):
        order_obj = self.env['purchase.order']
        for record in self.workorder_id:
            po = order_obj.search(
                [('state', '=', 'draft'), ('partner_id', '=', self.supplier.id),
                 ('company_id', '=', record.production_id.company_id.id)], limit=1)
            if po:
                self.purchase_order_line_create(po)
            else:
                po = order_obj.create({
                                        'partner_id': self.supplier.id,
                                        'payment_term_id': self.supplier.property_supplier_payment_term_id.id,
                                        'fiscal_position_id': self.supplier.property_account_position_id.id,
                                        'company_id': record.production_id.company_id.id,
                                        'date_order': fields.Datetime.now(),
                                        'date_planned': fields.Datetime.now()
                                        })
                self.purchase_order_line_create(po)
        return {'type': 'ir.actions.act_window_close'}

    
    def purchase_order_line_create(self, po):
        line_obj = self.env['purchase.order.line']
        workorder = self.workorder_id
        if workorder.subcontract_qty:
            if workorder.qty_produced > workorder.subcontract_qty:
                qty = workorder.qty_remaining - self.qty_subcontract
            else:
                qty = workorder.qty_production - workorder.subcontract_qty - self.qty_subcontract
        else:
            qty = workorder.qty_remaining - self.qty_subcontract
        vas = {
            'name': workorder.product_id.display_name,
            'product_id': workorder.service_product_id.id,
            'product_uom': workorder.service_product_id.uom_id.id,
            'product_qty': 1.0,
            'date_planned': workorder.production_id.date_planned_finished,
            'price_unit': 0.0,
            'workorder_id': workorder.id,
            'order_id': po.id,
            }
        if qty >= 0:
            po_line = line_obj.create(vas)
            po_line.onchange_product_id()
            po_line.product_qty = self.qty_subcontract
            po_line._onchange_quantity()
            po_line.name = workorder.product_id.display_name,
            if not po.origin:
                po.origin = workorder.production_id.name
            else:
                po.write({'origin': po.origin + ',' + workorder.production_id.name})
        else:
            raise UserError('不能超工单数委外')



