# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class MrpWorkshopTrace(models.TransientModel):
    _name = 'mrp.workshop.trace'

    mrp_no = fields.Char(string='製造單號')
    workorder_ids = fields.Many2many('mrp.workorder', string='工單清單')
    mrp_exist = fields.Boolean(string='Search mrp exist?')

    @api.onchange('mrp_no')
    def search_mrp(self):
        name = self.mrp_no.strip() if self.mrp_no else ''
        production_id = 0

        if name:
            production = self.env['mrp.production'].search([('name', 'like', f'%{name}%')], limit=1, order='name')
            production_id = production.id if any(production) else 0

        self.workorder_ids = self.env['mrp.workorder'].search([('production_id', '=', production_id)], order='id')
        self.mrp_exist = True if production_id else False
