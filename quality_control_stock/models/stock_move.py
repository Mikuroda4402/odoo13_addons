# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.quality_control.models.qc_trigger_line import\
    _filter_trigger_lines


class StockMove(models.Model):
    _inherit = 'stock.move'

    qc_line_ids = fields.One2many(comodel_name="qc.inspection", inverse_name='move_id', string='質檢單')
    qualified_amount = fields.Float('合格數量',compute='_compute_qualified_amount',
                                    digits='Product Unit of Measure')

    @api.depends('qc_line_ids', 'qc_line_ids.receiving_qty')
    def _compute_qualified_amount(self):
        for move in self:
            qc_line_ids = move.qc_line_ids.filtered(lambda q: q.state in ('success', 'failed') and q.receiving_qty > 0)
            qc_qty = 0.0
            for qc in qc_line_ids:
               qc_qty += qc.receiving_qty
            move.qualified_amount = qc_qty


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    qualified_amount = fields.Float('合格數量',related='move_id.qualified_amount', readonly=True,
                                    digits='Product Unit of Measure')


    def create_qa_order(self):
        inspection_model = self.env['qc.inspection']
        partner_id = self.move_id.partner_id
        picking_type_id = self.move_id.picking_id.picking_type_id
        qc_trigger = self.env['qc.trigger'].search(
            [('picking_type_id', '=', picking_type_id.id)])
        is_qc = self.product_id.is_qc or self.product_id.product_tmpl_id.is_qc or self.product_id.categ_id.is_qc
        picking_type_id = self.move_id.picking_id.picking_type_id
        if is_qc and picking_type_id.is_qc:
            trigger_lines = set()
            for model in ['qc.trigger.product_category_line',
                          'qc.trigger.product_template_line',
                          'qc.trigger.product_line']:
                partner = (partner_id
                           if qc_trigger.partner_selectable else False)
                trigger_lines = trigger_lines.union(
                    self.env[model].get_trigger_line_for_product(
                        qc_trigger, self.product_id, partner=partner))
            for trigger_line in _filter_trigger_lines(trigger_lines):
                qa_order = inspection_model._make_inspection(self.move_id, trigger_line)
                qa_order.write({'qty': self.qty_done})
