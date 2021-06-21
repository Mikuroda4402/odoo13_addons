# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    def _create_qc_trigger(self):
        self.ensure_one()

        qc_trigger = {
            'name': self.code + '-' + self.name,
            'company_id': self.company_id.id,
            'routing_id': self.id,
            'partner_selectable': False,
        }
        return self.env['qc.trigger'].sudo().create(qc_trigger)

    @api.model_create_multi
    def create(self, val_list):
        routing_ids = super(MrpRouting, self).create(val_list)
        routing_ids._create_qc_trigger()
        return routing_ids

    def write(self, vals):
        res = super(MrpRouting, self).write(vals)
        if vals.get('name'):
            qc_trigger_model = self.env['qc.trigger'].sudo()
            for rec in self:
                qc_triggers = qc_trigger_model.search(
                    [('routing_id', '=', rec.id)])
                qc_triggers.write({'name': self.code + '-' + self.name})
        return res


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    is_qc = fields.Boolean('质检')
    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.operation_line",
        inverse_name="operation_id",
        string="Quality control triggers")

    # @api.onchange('is_qc')
    # def onchange_is_qc(self):
    #     self.ensure_one()
    #     if self.is_qc:
    #         qc_trigger = self.env['qc.trigger'].search([('routing_id', '=', self.routing_id.id)])
    #         if not qc_trigger:
    #             vals = {
    #                     'name': self.routing_id.name,
    #                     'company_id': self.company_id.id,
    #                     'routing_id': self.routing_id.id,
    #                     'partner_selectable': False
    #             }
    #             qc_trigger_vals = self.env['qc.trigger'].create(vals)
    #             self.update({
    #                 'qc_triggers': [(6, 0, [qc_trigger_vals.id])],
    #             })
    #             # qc_trigger = self.env['qc.trigger'].sudo().create({
    #             #     'name': self.routing_id.name,
    #             #     'company_id': self.company_id.id,
    #             #     'routing_id': self.routing_id.id,
    #             #     'partner_selectable': False})
    #             # return qc_trigger

