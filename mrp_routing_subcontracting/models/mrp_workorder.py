# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    subcontract = fields.Boolean('委外', default=lambda self: self.operation_id.subcontract, help="委外工单")
    service_product_id = fields.Many2one('product.product', '委外服务',
                                         default=lambda self: self.operation_id.service_product_id.id,
                                         domain=[('type', '=', 'service')])
    supplier = fields.Many2one('res.partner', '供应商',
                               default=lambda self: self.operation_id.default_supplier.id,
                               domain=[('supplier', '=', True)])
    purchase_line_ids = fields.One2many('purchase.order.line', inverse_name='workorder_id', string='采购订单明细', readonly=True)
    subcontract_qty = fields.Float('委外数量', compute='_compute_subcontract_qty')
    subcontract_finished_qty = fields.Float('委外完成数量', compute='_compute_subcontract_finished_qty')


    @api.model
    def create(self, values):
        res = super(MrpWorkorder, self).create(values)
        res.subcontract = res.operation_id.subcontract
        res.service_product_id = res.operation_id.service_product_id
        res.supplier = res.operation_id.default_supplier
        return res

    @api.depends('purchase_line_ids.product_qty')
    def _compute_subcontract_qty(self):
        for work in self:
            work.subcontract_qty = 0
            if work.purchase_line_ids:
                work.subcontract_qty = sum(work.purchase_line_ids.filtered
                                           (lambda p: p.state not in ('cancel', 'draft', 'sent')).mapped('product_qty'))

    @api.depends('purchase_line_ids.qty_received')
    def _compute_subcontract_finished_qty(self):
        for work in self:
            work.subcontract_finished_qty = 0
            if work.purchase_line_ids:
                work.subcontract_finished_qty = sum(
                    work.purchase_line_ids.filtered(lambda p: p.order_id.state == 'purchase').mapped('qty_received'))

    
    def subcontract_order_finish(self):
        for wo in self:
            if wo.qty_producing> wo.qty_production - wo.qty_produced:
                raise UserError('完成数量不可大于未完工数量')
            else:
                if wo.purchase_line_ids:
                    #判断是否有可完成的采购订单
                    if not wo.purchase_line_ids.filtered(lambda p: p.state == 'purchase' and p.product_qty > p.qty_received):
                        raise UserError('没有可完成的委外采购订单')
                    else:
                        # 有可完成的采购订单完成数量写入第一条
                        po_line = wo.purchase_line_ids.filtered(
                            lambda p: p.state == 'purchase' and p.product_uom_qty > p.qty_received).sorted('date_planned')[0]
                        qty = po_line.qty_received + wo.qty_producing
                    if qty > po_line.product_qty:
                        raise ValidationError('委外订单数量为' + str(po_line.product_qty) + ',' + '超委外订单数量' + str(qty - po_line.product_qty))
                    else:
                        po_line.qty_received += wo.qty_producing
                        wo.record_production()
        return True

