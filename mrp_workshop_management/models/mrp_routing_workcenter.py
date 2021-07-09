# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MrpRoutingWorkCenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    temporary = fields.Boolean('臨時工序')

