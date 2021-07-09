# -*- coding: utf-8 -*-
import base64
from itertools import groupby

import xlrd

from odoo import models, fields, exceptions


class StockMovePurchaseDigi(models.Model):
    _inherit = "stock.move"
    Purchase_Digi = fields.Char('採購單號')


class StockImportPurchase(models.Model):
    _inherit = "stock.picking"

    data = fields.Binary()

    def get_partner(self, sheet):
        partner_all = set(sheet.row_values(0))
        partner = (i for i in partner_all)
        return partner

    def import_purchase(self):
        if self.data:
            xls = xlrd.open_workbook(filename=base64.decodebytes(self.data))
            sheet = xls.sheet_by_index(0)
            res = []
            ctx = self.id
            key = sheet.col_values(0)
            partner_all = self.get_partner(sheet)
            Picking = self.env['stock.picking']
            Stockmove = self.env['stock.move']
            product_obj = self.env['product.product']
            partner_obj = self.env['res.partner']
            stock_picking_type = self.env['stock.picking.type'].search([('name', '=', u'收貨'), ('warehouse_id', '=', 1)])
            for row in range(1, sheet.nrows):
                val = {}
                # field = sheet.row_values(row)
                # values = dict(zip(key,field))
                # val['partner'] = values['\u5ee0\u5546\u4ee3\u865f']
                partner_code = sheet.cell(row, 0).value
                min_date = sheet.cell(row, 2).value
                product_code = sheet.cell(row, 3).value
                purchase_qty = sheet.cell(row, 6).value
                purchase_ids = sheet.cell(row, 9).value
                product = product_obj.search([('default_code', '=', product_code)])
                val['partner'] = partner_code
                val['date'] = min_date
                val['product_id'] = product.id
                val['product_name'] = product.name
                val['uom'] = product.uom_id
                val['product_qty'] = purchase_qty
                val['digi'] = purchase_ids
                res.append(val)
            picking_value = groupby(res, lambda l: l['partner'])
            d = dict()
            for g, v in picking_value:
                d[g] = list(v)
                picking_value = d
            # return picking_value
            for partner in partner_all:
                partner_id = partner_obj.search([('ref_pcode', '=', partner)])
                val1 = {'partner_id': partner_id.id,
                        'stock_picking_type': stock_picking_type.id}
                picking = Picking.create(val1)
                for k in picking_value:
                    Q = k(partner)
                    for U in Q:
                        Stockmove.create({
                            "name": U['product_name'],
                            "product_id": U['product_id'],
                            "product_uom_qty": U['product_qty'],
                            "picking_id": picking.id,
                            "location_id": stock_picking_type.default_location_src_id,
                            "location_dest_id": stock_picking_type.default_location_dest_id,
                            "product_uom": U['uom'],
                            "origin": U['digi']
                        })
        else:
            raise exceptions.UserError('Upload Excel files first!')
