from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def stock_reserve(self):
        for move in self:
            if move.state not in ('draft', 'cancel', 'done'):
                move._action_assign()

    def do_un_stock_reserve(self):
        for move in self:
            if move.state not in ('draft', 'cancel', 'done'):
                move._do_unreserve()

    def do_cancel(self):
        """ Cancels production order, unfinished stock moves and set procurement
        orders in exception """
        for move in self:
            om = move.move_orig_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            if om:
                om._action_cancel()
                om.unlink()
            move.filtered(lambda x: x.state not in ('done', 'cancel'))._action_cancel()
            move.unlink()
    
    # def afresh_procurement(self):
    #     for move in self:
    #         new_move = move.copy()
    #         move.do_cancel()
    #         new_move._adjust_procure_method()
    #         new_move._action_confirm()

