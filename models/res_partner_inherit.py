# # -- coding: utf-8 --

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo import http
from odoo.http import request
from datetime import datetime


class Student(models.Model):
    _inherit = "res.partner"

    appointment_count = fields.Integer(string='Appointments', compute='_compute_appointment_count')
    prescription_count = fields.Integer(string='Prescriptions', compute='_compute_prescription_count')
    doctor_degree = fields.Char(string='Degree')
    doctor_specialization = fields.Char(string='Specialization')
    bmdc_no = fields.Char(string='BMDC No')
    weight = fields.Float(string='Weight')
    height = fields.Float(string='Height')
    gender = fields.Selection(
        [
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        
        ],
        string='Sex',
        tracking=True
    )
    date_of_birth = fields.Date(string='Date of Birth')
    blood_group = fields.Selection(
        [
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
            ('Unknown', 'Unknown')
        ],
        string='Blood Group',
        tracking=True
    )
    signature = fields.Binary(string='Signature')
    
    doc_dept_id = fields.Many2one('se.health.doc.departments', string='Department')

    def _compute_appointment_count(self):
        for rec in self:
            # Count the appointments only for the current partner
            rec.appointment_count = self.env['se.health.appoinement'].search_count([('patient_id', '=', rec.id)])

    def _compute_prescription_count(self):
        for rec in self:
            # Count the prescriptions only for the current partner
            rec.prescription_count = self.env['se.prescription.order'].search_count([('patient_id', '=', rec.id)])

    def action_view_appointment(self):
        action = self.env.ref('mini_clinic.action_se_appointment').read()[0]
        # Set domain to filter appointments for this partner (patient)
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action

    def action_view_prescription(self):
        action = self.env.ref('mini_clinic.action_se_prescription_order').read()[0]
        # Set domain to filter prescriptions for this partner (patient)
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


    
