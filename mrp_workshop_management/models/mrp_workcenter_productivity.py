# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    work_qty = fields.Float('報工數量', digits=dp.get_precision('Product Unit of Measure'))
    scrap_qty = fields.Float('報廢數量', digits=dp.get_precision('Product Unit of Measure'))
    unqa_qty = fields.Float('不合格數量', digits=dp.get_precision('Product Unit of Measure'))
    finished_qty = fields.Float('實際完工數量', digits=dp.get_precision('Product Unit of Measure'))
    confirm = fields.Boolean('確認', default=False)

    @api.onchange('work_qty', 'unqa_qty')
    def _onchange_work_qty(self):
        if self.work_qty < self.unqa_qty:
            raise UserError("報廢數量不能大於報工數量")
        self.finished_qty = self.work_qty - self.unqa_qty

    def button_task_finish(self):
        return self.write({'confirm': True})

