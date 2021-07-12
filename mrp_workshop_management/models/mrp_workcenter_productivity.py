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

    iot_number = fields.Char('IoT number', default='')
    remark = fields.Text('Remark')

    @api.model
    def create(self, vals_list):
        """
        建立生產日誌時定義批號，
        批號產生規則為關聯的工作中心代號 + 年月日 + 3碼流水號
        :param vals_list:
        :return:
        """
        production = self.env['mrp.production'].browse(vals_list['production_id'])
        production_code = production.pi_number

        ir_seq = self.env['ir.sequence']
        iot_number = ir_seq.next_by_code(production_code)
        if not iot_number:
            ir_seq.create({
                'name': production_code,
                'code': production_code,
                'implementation': 'no_gap',
                'active': True,
                'prefix': f'{production_code}%(y)s%(month)s%(day)s',
                'padding': 5,
                'number_increment': 1,
            })
            iot_number = ir_seq.next_by_code(production_code)

        vals_list['iot_number'] = iot_number
        return super(MrpWorkcenterProductivity, self).create(vals_list)
