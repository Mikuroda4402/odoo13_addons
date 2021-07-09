# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.fields import first
from odoo.exceptions import UserError

class QcInspection(models.Model):
    _inherit = "qc.inspection"

    picking_id = fields.Many2one(
        comodel_name="stock.picking", compute="_compute_picking", store=True
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", compute="_compute_lot", store=True
    )
    move_id = fields.Many2one(
        comodel_name="stock.move", compute="_compute_picking", store=True)
    partner_id = fields.Many2one('res.partner', related='picking_id.partner_id', string='客戶/供應商', store=True, readonly=True)

    def object_selection_values(self):
        result = super().object_selection_values()
        result.extend(
            [
                ("stock.picking", "Picking List"),
                ("stock.move", "Stock Move"),
                ("stock.production.lot", "Lot/Serial Number"),
            ]
        )
        return result

    @api.depends("object_id")
    def _compute_picking(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == "stock.move":
                    inspection.picking_id = inspection.object_id.picking_id
                    inspection.move_id = inspection.object_id.id
                elif inspection.object_id._name == "stock.picking":
                    inspection.picking_id = inspection.object_id
                    inspection.move_id = False
                elif inspection.object_id._name == "stock.move.line":
                    inspection.picking_id = inspection.object_id.picking_id
                    inspection.move_id = inspection.object_id.move_id
                else:
                    inspection.picking_id = False
                    inspection.move_id = False
            else:
                inspection.picking_id = False
                inspection.move_id = False

    @api.depends("object_id")
    def _compute_lot(self):
        moves = self.filtered(
            lambda i: i.object_id and i.object_id._name == "stock.move"
        ).mapped("object_id")
        move_lines = self.env["stock.move.line"].search(
            [("lot_id", "!=", False), ("move_id", "in", [move.id for move in moves])]
        )

        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == "stock.move.line":
                    inspection.lot_id = inspection.object_id.lot_id
                elif inspection.object_id._name == "stock.move":
                    inspection.lot_id = first(
                        move_lines.filtered(
                            lambda line: line.move_id == inspection.object_id
                        )
                    ).lot_id
                elif inspection.object_id._name == "stock.production.lot":
                    inspection.lot_id = inspection.object_id

    @api.depends("object_id")
    def _compute_product_id(self):
        """Overriden for getting the product from a stock move."""
        super(QcInspection, self)._compute_product_id()
        for qc in self:
            if qc.object_id:
                if qc.object_id._name == "stock.move":
                    qc.product_id = qc.object_id.product_id
                elif qc.object_id._name == "stock.move.line":
                    qc.product_id = qc.object_id.product_id
                elif qc.object_id._name == "stock.production.lot":
                    qc.product_id = qc.object_id.product_id

    @api.onchange("object_id")
    def onchange_object_id(self):
        if self.object_id:
            if self.object_id._name == "stock.move":
                self.qty = self.object_id.product_qty
            elif self.object_id._name == "stock.move.line":
                self.qty = self.object_id.product_qty

    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super()._prepare_inspection_header(object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == "stock.move.line":
            res["qty"] = object_ref.product_qty
        if object_ref and object_ref._name == "stock.move":
            res["qty"] = object_ref.product_uom_qty
        return res

    def action_confirm(self):
        for inspection in self:
            for line in inspection.inspection_lines:
                if line.question_type == 'qualitative':
                    if not line.qualitative_value:
                        raise UserError(
                            _("You should provide an answer for all "
                              "qualitative questions."))
                else:
                    if not line.uom_id:
                        raise UserError(
                            _("You should provide a unit of measure for "
                              "quantitative questions."))
            if inspection.qualification_rate > 100 or inspection.qualification_rate < 0:
                raise UserError('合格率不能大於100或者小於0.')
            if inspection.success:
                inspection.state = 'success'
            else:
                inspection.state = 'waiting'
            return super(QcInspection,self).action_confirm()

    @api.onchange('qualified_qty', 'qty_cr')
    def _onchange_qualification_rate(self):
        if self.qualification_rate > 100 or self.qualification_rate < 0:
            raise UserError('合格率不能大於100或者為負')
        if self.qualified_qty > 0:
            self.qualification_rate = self.qualified_qty / self.qty * 100
        self.receiving_qty = self.qualified_qty + self.qty_cr


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    picking_id = fields.Many2one(
        comodel_name="stock.picking", related="inspection_id.picking_id", store=True
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", related="inspection_id.lot_id", store=True
    )
