# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)
from odoo import api, fields, models, _
import re
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"
    _rec_name = 'name'

    partner_code = fields.Many2one('sale.partner.code', string='公司編號')
    sale_state = fields.Many2one('sale.partner.status', string=' 交易狀態')
    partner_class = fields.Many2one('sale.partner.class', string='等級')
    partner_source = fields.Many2one('sale.partner.source', string='客戶來源')
    source_note = fields.Text('備註')
    ref_pcode = fields.Char(string='廠商代號', copy=False, )
    short_name = fields.Char(string=u'簡稱', copy=False)
    fax = fields.Char(string=u'傳真', copy=False)


    @api.model
    def create(self, vals):
        if 'ref_pcode' in vals:
            if not vals['ref_pcode']:
                if vals['customer'] and not vals['supplier']:
                    vals['ref_pcode'] = self.env['ir.sequence'].next_by_code('partner.customer.number')

                if not vals['customer'] and vals['supplier']:
                    vals['ref_pcode'] = self.env['ir.sequence'].next_by_code('partner.supplier.number')

                if vals['customer'] and vals['supplier']:
                    vals['ref_pcode'] = self.env['ir.sequence'].next_by_code('partner.both.number')

                if not vals['customer'] and not vals['supplier']:
                    vals['ref_pcode'] = self.env['ir.sequence'].next_by_code('partner.default.number')

        return super(ResPartner, self).create(vals)

    @api.multi
    @api.depends('name', 'ref_pcode')
    def name_get(self):
        res = []

        for record in self:
            name = record.name
            if record.ref_pcode:
                name = "[%s] %s" % (record.ref_pcode, name)
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|', ('ref_pcode', operator, name), ('name', operator, name)] + args, limit=limit)

        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    # 驗證 Email 欄位是否正確
    @api.onchange('email_id')
    def validate_mail(self):
        if self.email_id:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email_id)
            if match == None:
                raise ValidationError(u'請重新輸入正確的Email Address格式')
