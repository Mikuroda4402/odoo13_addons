# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = 'qc.inspection'


    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super(QcInspection, self)._prepare_inspection_header(
            object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == 'mrp.production':
            res['qty'] = object_ref.product_qty
        if object_ref and object_ref._name == 'mrp.workcenter.productivity':
            res['qty'] = object_ref.work_qty
        return res

    @api.depends('object_id')
    def get_production(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == 'stock.move':
                    inspection.production_id = inspection.object_id.production_id
                elif inspection.object_id._name == 'mrp.production':
                    inspection.production_id = inspection.object_id
                elif inspection.object_id._name == 'mrp.workcenter.productivity':
                    inspection.workorder_id = inspection.object_id.workorder_id
                    inspection.production_id = inspection.workorder_id.production_id

    @api.depends('object_id')
    def _compute_product_id(self):
        """Overriden for getting the product from a manufacturing order."""
        for inspection in self:
            super(QcInspection, inspection)._compute_product_id()
            if inspection.object_id and\
                    inspection.object_id._name == 'mrp.production':
                inspection.product_id = inspection.object_id.product_id
            elif inspection.object_id and\
                inspection.object_id._name == 'mrp.workcenter.productivity':
                inspection.product_id = inspection.object_id.workorder_id.product_id


    def object_selection_values(self):
        objects = super(QcInspection, self).object_selection_values()
        objects.extend([
            ('mrp.production', 'Manufacturing Order'), ('mrp.workcenter.productivity', 'Job Order')])
        return objects


    def action_confirm(self):
        res = super(QcInspection, self).action_confirm()
        if self.object_id._name == 'mrp.workcenter.productivity':
            self.object_id.confirm = True
            self.object_id.scrap_qty = self.scrap_qty
            self.object_id.unqa_qty = self.qty - self.qualified_qty
            self.object_id.finished_qty = self.receiving_qty
            self.object_id.workorder_id.qty_producing += self.receiving_qty
        return res


    def action_cancel(self):
        res = super(QcInspection, self).action_cancel()
        if self.state in ('success', 'failed') and self.receiving_qty > 0 \
                and self.workorder_id.state != 'done':
            self.object_id.workorder_id.qty_producing -= self.receiving_qty
        return res



    production_id = fields.Many2one(
        comodel_name="mrp.production", compute="get_production", store=True)
    workorder_id = fields.Many2one('mrp.workorder', compute="get_production", store=True)
    operation_id = fields.Many2one('mrp.routing.workcenter', related='workorder_id.operation_id',string='工藝')



class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    production_id = fields.Many2one(
        comodel_name="mrp.production", related="inspection_id.production_id",
        store=True, string="Production order")
    workorder_id = fields.Many2one('mrp.workorder', related="inspection_id.workorder_id",
                                   store=True, string="Operation")