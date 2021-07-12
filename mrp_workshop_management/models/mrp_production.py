# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    workorder_ids = fields.One2many(readonly=False)

    
    def button_plan(self):
        res = super(MrpProduction, self).button_plan()
        self.set_next_wo_id()
        # self.date_planned_finished = self.workorder_ids[-1].date_planned_finished
        return res

    
    def set_next_wo_id(self):
        for production in self:
            # sequence = production.workorder_ids[0].sequence
            for order in production.workorder_ids:
                # if order.sequence == sequence:
                #     order.date_planned_start = production.date_planned_start
                #     order.date_planned_finished = order.date_planned_start + timedelta(minutes=order.duration_expected)
                wo = production.env['mrp.workorder']
                next_work_order_id = wo.search([('sequence', '=', order.sequence + 1),
                                                ('production_id', '=', order.production_id.id)], limit=1)

                if next_work_order_id:
                    order.next_work_order_id = next_work_order_id.id
                    # next_work_order_id.date_planned_start = fields.Datetime.from_string(order.date_planned_finished)
                    # next_work_order_id.date_planned_finished = fields.Datetime.from_string(next_work_order_id.date_planned_start) + \
                    #                                         relativedelta(minutes=next_work_order_id.duration_expected)
                else:
                    order.next_work_order_id = False
        return True

    def _workorders_create(self, bom, bom_data):
        """
        :param bom: in case of recursive boms: we could create work orders for child
                    BoMs
        """
        workorders = self.env['mrp.workorder']

        sequence = 0
        for operation in bom.routing_id.operation_ids.filtered(lambda o: not o.temporary):
            sequence += 1
            workorder = workorders.create({
                'name': operation.workcenter_id.sequence_id.next_by_id(),
                'production_id': self.id,
                'sequence': sequence,
                'workcenter_id': operation.workcenter_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'operation_id': operation.id,
                'state': len(workorders) == 0 and 'ready' or 'pending',
                'qty_producing': 0,
                'consumption': self.bom_id.consumption,
            })
            if workorders:
                workorders[-1].next_work_order_id = workorder.id
                workorders[-1]._start_nextworkorder()
            workorders += workorder

            moves_raw = self.move_raw_ids.filtered(lambda move: move.operation_id == operation and move.bom_line_id.bom_id.routing_id == bom.routing_id)
            moves_finished = self.move_finished_ids.filtered(lambda move: move.operation_id == operation)

            # - Raw moves from a BoM where a routing was set but no operation was precised should
            #   be consumed at the last workorder of the linked routing.
            # - Raw moves from a BoM where no rounting was set should be consumed at the last
            #   workorder of the main routing.
            if len(workorders) == len(bom.routing_id.operation_ids.filtered(lambda o: not o.temporary)):
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id and move.bom_line_id.bom_id.routing_id == bom.routing_id)
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.workorder_id and not move.bom_line_id.bom_id.routing_id)

                moves_finished |= self.move_finished_ids.filtered(lambda move: move.product_id != self.product_id and not move.operation_id)

            moves_raw.mapped('move_line_ids').write({'workorder_id': workorder.id})
            (moves_finished | moves_raw).write({'workorder_id': workorder.id})

            workorder._generate_wo_lines()
        return workorders

    pi_number = fields.Char(string=_('Pi number'), required=True, default='')
