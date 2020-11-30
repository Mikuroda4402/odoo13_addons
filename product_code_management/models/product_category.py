# _*_ coding: utf-8 _*_

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = "product.category"

    categ_code = fields.Char(u"物料分类码", required=True)
    variants_length = fields.Integer(u"产品变型流水号长度", default=3, required=True)
