# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class QcTriggerOperationLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.operation_line"

    operation_id = fields.Many2one(comodel_name="mrp.routing.workcenter")

    def get_trigger_line_for_product(self, trigger, operation, partner=False):
        trigger_lines = super(QcTriggerOperationLine, self).get_trigger_line_for_product(trigger, operation,
                                                                                           partner=partner)
        for trigger_line in operation.qc_triggers.filtered(
                lambda r: r.trigger == trigger and (
                        not r.partners or not partner or
                        partner.commercial_partner_id in r.partners) and
                          r.test.active):
            trigger_lines.add(trigger_line)
        return trigger_lines

    @api.model
    def create(self, vals):
        operation = self.env['mrp.routing.workcenter'].search([('id', '=', vals.get('operation_id'))])
        trigger = self.env['qc.trigger'].search([('routing_id', '=', operation.routing_id.id)])
        if trigger:
            vals['trigger'] = trigger[0].id
        return super(QcTriggerOperationLine, self).create(vals)
