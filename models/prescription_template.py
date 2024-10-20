# -- coding: utf-8 --
from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SePrescriptionTemplate(models.Model):
    _name = 'se.prescription.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Prescription Template'

    name = fields.Char(string='Template Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    note = fields.Text(string='Note')
    doctor_id = fields.Many2one('res.partner', string='Doctor', required=True, domain=[('partner_type', '=', 'doctor')])
    disease_ids = fields.Many2many('se.prescription.disease', string='Diseases')
    suggestions_ids = fields.Many2many('se.prescription.suggestions', string='Suggestions')
    diagnosis_ids = fields.Many2many('se.prescription.diagnosis', string='Diagnosis')
    plan_ids = fields.Many2many('se.prescription.plan', string='Plan')
    medicine_ids = fields.One2many('se.prescription.template.line', 'template_id', string='Medicines')
    lab_test_ids = fields.Many2many('se.prescription.lab.test', string='Lab Tests')
    

class SePrescriptionTemplateLine(models.Model):
    _name = 'se.prescription.template.line'
    _description = 'Prescription Template Line'

    template_id = fields.Many2one('se.prescription.template', string='Prescription Template')
    product_id = fields.Many2one('product.product', string='Medicine', required=True, domain=[('is_medicine', '=', True)])
    quantity = fields.Float(string='Quantity', default=1.0)
    dose = fields.Float('Dosage (mg)', default=1.0)
    days = fields.Float("Days", default=1.0)
    qty_per_day = fields.Selection([('1', '1-1-1'),
            ('2', '1-0-0'),
            ('3', '0-1-0'),
            ('4', '0-0-1'),
            ('5', '1-1-0'),
            ('6', '0-1-1'),
            ('7', '1-0-1'),
            ('8', '1-0-1-1'),
            ('9', '0-1-0-1'),
            ('10', '1-0-0-1'),
            ('11', '1-1-0-1'),
            ('12', '1-0-1-0'),
            ('13', '0-1-1-0'),
            ('14', '1-1-1-0'),
            ('15', '1-1-0-0'),
            ('16', '0-1-1-1'),
            ('17', '1-1-1-1'),
            ('18', '1-0-1-1-1'),
            ('19', '1-1-0-1-1'),
            ('20', '1-1-1-0-1'),
            ('21', '1-1-1-1-0'),
            ('22', '0-1-1-1-1'),
            ('23', '1-1-1-1-1')], string='Qty/Day',default='1')
    dose_suggestions = fields.Many2one('se.prescription.dose.suggestions', string='Dose Suggestions')

