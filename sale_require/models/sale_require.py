# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare


class SaleRequire(models.Model):
    _name = 'sale.require'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    # state = fields.Selection([
    #     ('draft', 'Quotation'),
    #     ('sent', 'Quotation Sent'),
    #     ('sale', 'Sales Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    state = fields.Selection([
        ('Y', 'Y'),
        ('N', 'N'), ], string='成交與否')
    create_date = fields.Datetime(string='Creation Date', readonly=True, index=True,
                                  help="Date on which sales order is created.")
    publish_user_id = fields.Many2one('res.users', string='發文者')
    create_user_id = fields.Many2one(
        'res.users', string='建立者', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: [('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)])
    share_n = fields.Boolean('不分享')
    share_y = fields.Many2many('res.users', string='分享給指定人員')
    addressee_user_id = fields.Many2one('res.users', string='受文者')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
         )
    #domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    country_id = fields.Many2one('res.partner', string='國家', readonly=True, related='partner_id.country_id')
    category_id = fields.Many2one('require.category', string='分類')
    require_spec = fields.Many2many('sale.require.spec', string='索取')
    other_require = fields.Text('其他')
    require_line = fields.One2many('sale.require.line', 'require_id', string='Require Lines',
                                   states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                   auto_join=True)
    standard_note = fields.Text('規格')
    note = fields.Text('備註')


    attachment_number = fields.Integer(compute='_compute_attachment_number', string='附件上傳')

    # @api.model
    # def create(self, vals):
    # if vals.get('name', _('New')) == _('New'):
    #     vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
    #         'sale.require', sequence_date=create_date) or _('New')
    #     else:
    #         vals['name'] = self.env['ir.sequence'].next_by_code('sale.require', sequence_date=create_date) or _('New')
    #
    #
    # result = super(SaleRequire, self).create(vals)
    # return result

    def attachment_image_preview(self):
        self.ensure_one()
        # domain可以过滤指定的附件类型 （mimetype）
        domain = [('res_model', '=', self._name), ('res_id', '=', self.id)]
        return {
            'domain': domain,
            'res_model': 'ir.attachment',
            'name': u'附件管理',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 20,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    def _compute_attachment_number(self):
        """附件上传"""
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'sale_require'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense.id, 0)

    def action_get_attachment_view(self):
        """附件上传动作视图"""
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'sale_require'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'sale_require', 'default_res_id': self.id}
        return res


class SaleRequireLine(models.Model):
    _name = 'sale.require.line'

    require_id = fields.Many2one('sale.require', string='Order Reference', required=True, ondelete='cascade',
                                 index=True, copy=False)
    name = fields.Text(string='品名', required=True)
    sequence = fields.Integer(string='項次', default=10)
    require_category_id = fields.Many2one('sale.require.line.category', string='類別', required=True, copy=True)
    require_qty = fields.Float(string='數量', required=True, default=1.0)
    sample_qty = fields.Float(string='樣品數', required=True, default=1.0)
    pi_no = fields.Text('PI NO.')
    state = fields.Selection([
        ('Y', 'Y'),
        ('N', 'N'), ], string='成交與否')
