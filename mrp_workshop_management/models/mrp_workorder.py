# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    _order = 'sequence, id'

    name = fields.Char(copy=False, readonly=True, default=lambda self: _('New'))
    date_planned_start = fields.Datetime(default=fields.Datetime.now)
    sequence = fields.Integer('序號')
    routing_id = fields.Many2one('mrp.routing', related='production_id.routing_id', readonly=True)

    @api.onchange('operation_id')
    def _onchange_operation(self):
        if self.operation_id:
            self.workcenter_id = self.operation_id.workcenter_id

    def button_compute_done_qty(self):
        if self.time_ids.filtered(lambda t: not t.confirm):
            qty_producing = sum(self.time_ids.filtered(lambda t: not t.confirm).mapped('finished_qty'))
            return self.write({'qty_producing': qty_producing})

    def button_pending(self):
        for order in self:
            wo = order.time_ids.filtered(lambda t: t.work_qty == 0)
            if wo:
                raise UserError('報工單未填入數量')
            wo = order.time_ids.filtered(lambda w: not w.date_end)[0]
            if wo:
                wo.date_end = datetime.now()
        return super(MrpWorkorder, self).button_pending()

    def button_confirm_qty(self):
        wo = self.time_ids.filtered(lambda t: t.work_qty == 0)
        if wo:
            raise UserError('報工單未填入數量')
        self.button_compute_done_qty()
        return self.time_ids.filtered(lambda t: not t.confirm).write({'confirm': True})

    def unlink(self):
        for wo in self:
            if wo.qty_produced > 0:
                raise UserError('已有完工數，此單據只能取消不能進行刪除')
        return super(MrpWorkorder, self).unlink()

    def copy(self, default=None):
        res = super(MrpWorkorder, self).copy(default)
        res.qty_produced = 0
        return res

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            workcenter_id = values.get('workcenter_id')
            workcenter_id = self.env['mrp.workcenter'].browse(workcenter_id)
            if workcenter_id:
                values['name'] = workcenter_id.sequence_id.next_by_id()
        res = super(MrpWorkorder, self).create(values)
        return res

    def button_confirm(self):
        return self.write({'state': 'ready'})

    def button_unblock(self):
        res = super(MrpWorkorder, self).button_unblock()
        if self.time_ids.filtered(lambda t: t.work_qty == 0):
            raise UserError('報工單未填入數量')
        return res

    remark = fields.Text(string='備註')
