# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MrpWorkCenter(models.Model):
    _inherit = 'mrp.workcenter'

    sequence_id = fields.Many2one('ir.sequence', '工單編號')

