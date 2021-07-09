# _*_ coding: utf-8 _*_
import base64
from itertools import groupby

import xlrd

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

# xlrd cell formats
XL_CELL_EMPTY = 0  # Python value:empty string u''
XL_CELL_TEXT = 1  # Python value:a Unicode string
XL_CELL_NUMBER = 2  # Python value:float
XL_CELL_DATE = 3  # Python value:float
XL_CELL_BOOLEAN = 4  # Python value:int; 1 means TRUE, 0 means FALSE
XL_CELL_ERROR = 5  # Python value:int representing internal Excel codes; for a text representation, refer to the supplied dictionary error_text_from_code
XL_CELL_BLANK = 6  # Python value:empty string u''. Note: this type will appear only when open_workbook(..., formatting_info=True) is used.


class StockImportPurchase(models.Model):
    _name = "stock_import_picking.stock_import_picking"

    data = fields.Binary()

    def get_partner(self, sheet):
        partner_all = set(sheet.col_values(0))
        partner = [i for i in partner_all]
        del partner[0]
        return partner

    def import_purchase(self):
        if self.data:
            xls = xlrd.open_workbook(file_contents=base64.decodebytes(self.data))
            sheet = xls.sheet_by_index(0)
            res = []
            picking_list = list()
            ctx = self.id
            key = sheet.col_values(0)
            partner_all = self.get_partner(sheet)
            Picking = self.env['stock.picking']
            Stockmove = self.env['stock.move']
            product_obj = self.env['product.product']
            partner_obj = self.env['res.partner']
            stock_picking_type = self.env['stock.picking.type'].search([('name', '=', u'接收'), ('warehouse_id', '=', 1)])
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
                # val['partner'] = partner_code
                # val['date'] = min_date
                # val['product_code'] = product_code
                # val['product_qty'] = purchase_qty
                # val['digi'] = purchase_ids
                # res.append(val)
                val['partner'] = partner_code
                val['date'] = min_date
                val['product_id'] = product.id
                val['product_name'] = product.name
                val['uom'] = product.uom_id.id
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
                partner_id = partner_obj.search([('no', '=', partner)])
                val1 = {'partner_id': partner_id.id,
                        'stock_picking_type': stock_picking_type.id}
                picking = Picking.create(val1)
                picking_list.append(picking.id)
                move_val = picking_value[partner]
                for move in move_val:
                    Stockmove.create({
                        "name": move['product_name'],
                        "product_id": move['product_id'],
                        "product_uom_qty": move['product_qty'],
                        "picking_id": picking.id,
                        "location_id": stock_picking_type.default_location_src_id.id,
                        "location_dest_id": stock_picking_type.default_location_dest_id.id,
                        "product_uom": move['uom'],
                        "origin": move['digi']
                    })
            ready_picking = Picking.browse(picking_list)
            ready_picking.action_confirmed()
        else:
            raise UserError(_('Upload Excel files first!'))
