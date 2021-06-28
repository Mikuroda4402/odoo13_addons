# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2019 Andrii Skrypka
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.quality_control.models.qc_trigger_line import _filter_trigger_lines
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    qc_inspections_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="picking_id",
        copy=False,
        string="Inspections",
        help=_("Inspections related to this picking."),
    )
    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Created inspections"
    )
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Done inspections"
    )
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections OK"
    )
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections failed"
    )

    @api.depends("qc_inspections_ids", "qc_inspections_ids.state")
    def _compute_count_inspections(self):
        data = self.env["qc.inspection"].read_group(
            [("id", "in", self.mapped("qc_inspections_ids").ids)],
            ["picking_id", "state"],
            ["picking_id", "state"],
            lazy=False,
        )
        picking_data = {}
        for d in data:
            picking_data.setdefault(d["picking_id"][0], {}).setdefault(d["state"], 0)
            picking_data[d["picking_id"][0]][d["state"]] += d["__count"]
        for picking in self:
            count_data = picking_data.get(picking.id, {})
            picking.created_inspections = sum(count_data.values())
            picking.passed_inspections = count_data.get("success", 0)
            picking.failed_inspections = count_data.get("failed", 0)
            picking.done_inspections = (
                picking.passed_inspections + picking.failed_inspections
            )

    def create_qa_order(self):
        inspection_model = self.env['qc.inspection']
        qc_trigger = self.env['qc.trigger'].search(
            [('picking_type_id', '=', self.picking_type_id.id)])
        if self.picking_type_id.is_qc:
            for operation in self.move_lines.filtered(lambda m: m.quantity_done > 0):
                is_qc = operation.product_id.product_tmpl_id.is_qc or operation.product_id.categ_id.is_qc
                if is_qc:
                    trigger_lines = set()
                    for model in ['qc.trigger.product_category_line',
                                  'qc.trigger.product_template_line',
                                  'qc.trigger.product_line']:
                        partner = (self.partner_id
                                   if qc_trigger.partner_selectable else False)
                        trigger_lines = trigger_lines.union(
                            self.env[model].get_trigger_line_for_product(
                                qc_trigger, operation.product_id, partner=partner))
                    for trigger_line in _filter_trigger_lines(trigger_lines):
                        order = inspection_model._make_inspection(operation, trigger_line)
                        order.write({'qty': operation.quantity_done})

    def action_done(self):
        if self.picking_type_id.is_qc:
            for move in self.move_lines:
                is_qc = move.product_id.is_qc or move.product_id.product_tmpl_id.is_qc or move.product_id.categ_id.is_qc
                if move.quantity_done > move.qualified_amount and is_qc :
                    raise ValidationError(_(move.product_id.display_name + '總數量' + str(move.quantity_done) + '大於合格數量' + str(move.qualified_amount)))
        return super(StockPicking, self).action_done()