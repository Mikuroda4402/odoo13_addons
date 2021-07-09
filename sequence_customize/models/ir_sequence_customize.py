# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime

class sequence(models.Model):
    _inherit = 'ir.sequence'

    reset_setting = fields.Selection([('day','每日重置'),('month','每月重置'),('year','每年重置')],'重置時間')
    sl_yesterday = fields.Date(string="昨天", default=str(datetime.datetime.strptime(datetime.date.today().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1)))

    def _next(self):
        today = datetime.date.today().strftime('%Y-%m-%d')
        year = str(datetime.datetime.strptime(today, '%Y-%m-%d').year)
        month = str(datetime.datetime.strptime(today, '%Y-%m-%d').month)
        day = str(datetime.datetime.strptime(today, '%Y-%m-%d').day)
        if not self.sl_yesterday:
            self.sl_yesterday = today
        if str(today) != str(datetime.datetime.strptime(str(self.sl_yesterday), '%Y-%m-%d')):
            if str(datetime.datetime.strptime(str(self.sl_yesterday), '%Y-%m-%d').year) != year and self.reset_setting == 'year':
                self.number_next_actual = 1
            elif str(datetime.datetime.strptime(str(self.sl_yesterday), '%Y-%m-%d').month) != month and self.reset_setting == 'month':
                self.number_next_actual = 1
            elif str(datetime.datetime.strptime(str(self.sl_yesterday), '%Y-%m-%d').day) != day and self.reset_setting == 'day':
                self.number_next_actual = 1
            self.sl_yesterday = today
        result = super(sequence, self)._next()
        return result

    @api.model
    def create(self, vals):
        res_id = super(sequence, self).create(vals)
        today = datetime.date.today().strftime('%Y-%m-%d')
        res_id.sl_yesterday = today
        return res_id