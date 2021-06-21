# _*_ coding: utf-8 _*_

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tmpl_code = fields.Char(u"产品模板编码",readonly=True)
    variants_length = fields.Integer(u"产品变型流水号长度", related="categ_id.variants_length", required=True)

    @api.model
    def create(self, vals):
        categ = self.env["product.category"].browse(vals.get("categ_id"))
        vals["tmpl_code"] = self.get_serial_number(categ.categ_code)
        return super(ProductTemplate, self).create(vals)

    
    def write(self, vals):
        if "categ_id" in vals:
            categ = self.env["product.category"].browse(vals.get("categ_id"))
            vals["tmpl_code"] = self.get_serial_number(categ.categ_code)
        return super(ProductTemplate, self).write(vals)

    @api.model
    def get_serial_number(self, categ_code):
        if not categ_code:
            return ""
        length = 5
        Sequence = self.env["ir.sequence"]
        sequence = Sequence.search([("code", "=", categ_code)])
        if not sequence:
            sequence = Sequence.create({
                "code": categ_code,
                "name": u"产品模板编码序列",
                "padding": 12
            })
        next_number = sequence.next_by_code(categ_code)
        format_str = u"%%0%dd" % length
        return categ_code + (format_str % int(next_number))

    def _create_variant_ids(self):
        res = super(ProductTemplate, self)._create_variant_ids()
        for product in self.product_variant_ids:
            if not product.default_code:
                product.default_code = product.get_serial_number(self.tmpl_code, self.variants_length)
        return res