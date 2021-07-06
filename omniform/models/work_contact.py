# -*- coding: utf-8 -*-
from odoo import api, models, fields
from datetime import datetime, timedelta


class WorkContact(models.Model):
    _name = 'work.contact'
    _order = 'priority, id desc'
    _description = '工作聯繫單'
    _rec_name = 'name'

    def _get_status(self):
        if self.manager_id.id != self.env.user.id and self.user_id.id != self.env.user.id:
            self.is_readonly = True
        else:
            self.is_readonly = False

    def review_content_status(self):
        if self.manager_id.id != self.env.user.id:
            self.review_content_readonly = True
        else:
            self.review_content_readonly = False

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    name = fields.Char(string='單號')
    is_readonly = fields.Boolean(compute=_get_status)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='填單人員', default=_default_employee_id, readonly=True)
    user_id = fields.Many2one('res.users', related='employee_id.user_id')
    manager_id = fields.Many2one(comodel_name='res.users', related='employee_id.parent_id.user_id', readonly=True, string='上級主管')
    recipient_ids = fields.Many2many('hr.employee', relation="work_contact_employee_rec_rel", string='收件者')
    est_cmplt_date = fields.Date(string='預計完成日')
    subject = fields.Char(string='主旨')
    priority = fields.Selection(selection=[('1', '特急'), ('2', '高'), ('3', '普通')], string='優先順序', default='3')
    state = fields.Selection(selection=[('1', '草稿'), ('2', '主管批准'), ('3', '進行中'), ('4', '已完成'), ('5', '退回')], string='狀態', default='1')
    content = fields.Html(string='內容', default='')
    reply_content = fields.Html(string='回覆', default='')
    review_content_readonly = fields.Boolean(compute=review_content_status)
    review_content = fields.Html(string='審核內容')
    attachment_ids = fields.Many2many('ir.attachment', string='附件')
    work_contact_id = fields.Many2one('work.contact', string='聯繫主單', ondelete='cascade')
    line_ids = fields.One2many('work.contact', 'work_contact_id', string='聯繫子單')
    reply_count = fields.Integer(compute='compute_reply_count')

    @api.depends('line_ids')
    def compute_reply_count(self):
        self.reply_count = len(self.line_ids)
        return True

    def close_contact(self):
        self.state = '4'

    def submit_contact(self):
        self.state = '2'

    def approve_contact(self):
        self.state = '3'

    def set_draft(self):
        self.state = '1'

    def reject_contact(self):
        self.state = '5'

    def write(self, vals):
        if 'recipient_ids' in vals:
            if vals['recipient_ids'][0][2] != self.recipient_ids.ids:
                for line in self.line_ids:
                    line.recipient_ids = [(6, 0, vals['recipient_ids'][0][2])]
        if 'state' in vals:
            if vals['state'] != self.state and vals['state'] == '4':
                for line in self.line_ids:
                    line.state = vals['state']
        return super(WorkContact, self).write(vals)

    def sub_work_contact(self):
        action = self.env.ref('omniform.sub_work_contact_act').read()[0]
        content = '\n' + '-' * 40 + '\n' + self.reply_content if self.reply_content else self.content
        action['context'] = {
            'tree_view_ref': 'omniform.sub_work_contact_tree', 'form_view_ref': 'omniform.sub_work_contact_form',
            'search_view_ref': 'omniform.sub_work_contact_search', 'default_recipient_ids': [(6, 0, self.recipient_ids.ids)],
            'default_content': content, 'default_est_cmplt_date': self.est_cmplt_date, 'default_subject': self.subject,
            'default_work_contact_id': self.id, 'default_state': '3'}
        action['domain'] = []
        action['domain'] = [('work_contact_id', '=', self.id)]
        return action

    @api.model
    def create(self, vals):
        res_id = super(WorkContact, self).create(vals)
        seq_id = self.env['ir.sequence'].sudo().search([('code', '=', 'work.contact')], limit=1)
        number_next_actual = str(seq_id.number_next_actual).zfill(seq_id.padding)
        year, month = (datetime.now() + timedelta(hours=8)).strftime('%Y'), (datetime.now() + timedelta(hours=8)).strftime('%m')
        res_id.name = '%s%s' % (year, str(month).zfill(2)) + number_next_actual
        seq_id.number_next_actual += seq_id.number_increment
        return res_id
