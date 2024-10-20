# -- coding: utf-8 --
from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


# class SeDoctor(models.Model):
#     _name = 'se.doctor'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = 'Doctor'

#     name = fields.Char(string='Name', required=True)
#     active = fields.Boolean(string='Active', default=True)
#     user_id = fields.Many2one('res.users', string='User', required=True)
#     partner_id = fields.Many2one('res.partner', string='Partner', required=True)
#     experience = fields.Integer(string='Experience (in years)')
#     phone = fields.Char(string='Phone' )
#     doctor_degree = fields.Char(string='Degree')
#     doctor_specialization = fields.Char(string='Specialization')
#     bmdc_no = fields.Char(string='BMDC No')
#     gender = fields.Selection(
#         [
#             ('male', 'Male'),
#             ('female', 'Female'),
#             ('other', 'Other')
        
#         ],
#         string='Sex',
#         tracking=True
#     )
#     signature = fields.Binary(string='Signature')
    
#     doc_dept_id = fields.Many2one('se.health.doc.departments', string='Department')
    