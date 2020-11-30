# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RequireCategory(models.Model):
    _name = 'require.category'

    name = fields.Char(string='類別')


class SaleRequireLineCategory(models.Model):
    _name = 'sale.require.line.category'

    name = fields.Char(string='類別')


class SaleRequireWhat(models.Model):
    _name = 'sale.require.spec'

    name = fields.Char(string='索取')


class SalePartnerCode(models.Model):
    _name = 'sale.partner.code'

    name = fields.Char('公司編號')


class SalePartnerClass(models.Model):
    _name = 'sale.partner.status'

    name = fields.Char('交易狀態')


class SalePartnerSource(models.Model):
    _name = 'sale.partner.class'

    name = fields.Char('等級')


class PartnerNumber(models.Model):
    _name = 'partner.number'

    categ_code = fields.Char(u"客戶編碼", required=True)


variants_length = fields.Integer(u"流水號長度", default=3, required=True)

# @api.model
# def get_serial_number(self, categ_code, length):
#     if not categ_code:
#         return ""
#     Sequence = self.env["ir.sequence"]
#     sequence = Sequence.search([("code", "=", categ_code)])
#     if not sequence:
#         sequence = Sequence.create({
#             "code": categ_code,
#             "name": u"产品编码序列",
#             "padding": 10
#         })
#     next_number = sequence.next_by_code(categ_code)
#     format_str = u"%%0%dd" % length
#     return categ_code + (format_str % int(next_number))
