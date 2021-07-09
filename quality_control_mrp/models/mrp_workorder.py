# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons.quality_control.models.qc_trigger_line import \
    _filter_trigger_lines
from odoo.exceptions import UserError, ValidationError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.depends('qc_inspections_ids', 'qc_inspections_ids.state')
    def _compute_count_inspections(self):
        for wo in self:
            wo.created_inspections = len(wo.qc_inspections_ids)
            wo.passed_inspections = \
                len([x for x in wo.qc_inspections_ids
                     if x.state == 'success'])
            wo.failed_inspections = \
                len([x for x in wo.qc_inspections_ids
                     if x.state == 'failed'])
            wo.done_inspections = \
                (wo.passed_inspections + wo.failed_inspections)

    qc_inspections_ids = fields.One2many(
        comodel_name='qc.inspection', inverse_name='workorder_id', copy=False,
        string='Inspections', help=_("Inspections related to this picking."))
    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="質檢單")
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="已完成的質檢單")
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="合格的質檢單")
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="不合格的質檢單")
    qc_state = fields.Boolean(compute='compute_qc_state')
    is_qc = fields.Boolean('質檢', related='operation_id.is_qc', readonly=True, store=True)

    def create_qc_order(self):
        if self.is_qc:
            inspection_model = self.env['qc.inspection']
            qc_trigger = self.env['qc.trigger'].search(
                [('routing_id', '=', self.operation_id.routing_id.id)])
            for time in self.time_ids.filtered(lambda t: t.qc_state == 'un_qc' and t.work_qty > 0):
                if len(self.qc_inspections_ids.filtered(lambda q: q.object_id and q.object_id.id == time.id
                                                                  and q.state != 'cancel')) > 1:
                    raise UserError('不能重複建立質檢單')
                trigger_lines = set()
                partner = False
                # for model in ['qc.trigger.operation_line']:
                trigger_lines = trigger_lines.union(
                    self.env['qc.trigger.operation_line'].get_trigger_line_for_product(
                        qc_trigger, time.workorder_id.operation_id, partner=partner))
                for trigger_line in _filter_trigger_lines(trigger_lines):
                    inspection_model._make_inspection(time, trigger_line)

    @api.depends('time_ids', 'time_ids.qc_state')
    def compute_qc_state(self):
        for wo in self:
            if not wo.time_ids:
                wo.qc_state = False
            else:
                if wo.time_ids.filtered(lambda t: t.qc_state in ('un_qc', 'progress')):
                    wo.qc_state = False
                elif wo.time_ids.filtered(lambda t: t.qc_state not in ('un_qc', 'progress')):
                    wo.qc_state = True

    def button_compute_done_qty(self):
        if self.time_ids.filtered(lambda t: t.qc_state in ('process', 'un_qc')) and self.is_qc:
            time_line = self.time_ids.filtered(lambda t: t.qc_state in ('process', 'un_qc'))
            time_line.finished_qty = 0.0
            raise UserError('有質檢中的報工單，需等待質檢完成')
        super(MrpWorkorder, self).button_compute_done_qty()

    def record_production(self):
        if self.time_ids.filtered(lambda t: t.qc_state in ('process', 'un_qc')) and self.is_qc:
            raise UserError('有質檢中的報工單，需等待質檢完成')
        return super(MrpWorkorder, self).record_production()


class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    def get_default_loss(self):
        loss = self.env['mrp.workcenter.productivity.loss'].search([], limit=1)
        return loss

    qc_state = fields.Selection([('un_qc', '未質檢'),
                                 ('progress', '質檢中'),
                                 ('finished', '已質檢')],
                                compute='compute_qc_state', string='質檢狀態')
    is_qc = fields.Boolean(related='workorder_id.is_qc')
    loss_id = fields.Many2one(default=get_default_loss)

    @api.depends('workorder_id.qc_inspections_ids', 'workorder_id.qc_inspections_ids.state')
    def compute_qc_state(self):
        for mp in self:
            if not mp.workorder_id.qc_inspections_ids:
                mp.qc_state = 'un_qc'
            else:
                if not mp.workorder_id.qc_inspections_ids. \
                        filtered(lambda q: q.object_id and q.object_id.id == mp.id) \
                        or mp.workorder_id.qc_inspections_ids. \
                        filtered(lambda q: q.object_id and q.object_id.id == mp.id
                                           and q.state not in ('waiting', 'ready', 'success', 'failed')):
                    mp.qc_state = 'un_qc'
                if mp.workorder_id.qc_inspections_ids.filtered \
                            (lambda q: q.object_id and q.object_id.id == mp.id and q.state in ('waiting', 'ready')):
                    mp.qc_state = 'progress'
                elif mp.workorder_id.qc_inspections_ids.filtered(lambda q: q.object_id and q.object_id.id == mp.id
                                                                           and q.state in ('success', 'failed')):
                    mp.qc_state = 'finished'

    def unlink(self):
        for mw in self:
            if mw.workorder_id.qc_inspections_ids. \
                    filtered(lambda q: q.object_id and q.object_id.id == mw.id
                                       and q.state in ('waiting', 'ready', 'success', 'failed')):
                raise UserError('經過質檢的報工單不允許刪除，若要刪除請先取消質檢單')
        return super(MrpWorkcenterProductivity, self).unlink()
