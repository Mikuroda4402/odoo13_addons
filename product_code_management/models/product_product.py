# _*_ coding: utf-8 _*_

from odoo import models, fields, api


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        template = self.env["product.template"].browse(vals.get("product_tmpl_id"))
        vals["default_code"] = self.get_serial_number(template.tmpl_code,template.variants_length)
        return super(Product, self).create(vals)


    def write(self, vals):
        if "product_templ_id" in vals:
            template = self.env["product.template"].browse(vals.get("product_tmpl_id"))
            vals["default_code"] = self.get_serial_number(template.tmpl_code, template.variants_length)
        return super(Product, self).write(vals)

    @api.model
    def get_serial_number(self, categ_code, length):
        if not categ_code:
            return ""
        Sequence = self.env["ir.sequence"]
        sequence = Sequence.search([("code", "=", categ_code)])
        if not sequence:
            sequence = Sequence.create({
                "code": categ_code,
                "name": u"产品编码序列",
                "padding": 10
            })
        next_number = sequence.next_by_code(categ_code)
        format_str = u"%%0%dd" % length
        return categ_code + (format_str % int(next_number))
