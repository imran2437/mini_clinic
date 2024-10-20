# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SePrescriptionSuggestions(models.Model):
    _name = 'se.prescription.suggestions'
    _description = "Prescription Suggestions"

    name = fields.Char('Name')
    
class SePrescriptionDiagnosis(models.Model):
    _name = 'se.prescription.diagnosis'
    _description = "Prescription Diagnosis"

    name = fields.Char('Name')

    

class SePrescriptionPlan(models.Model):
    _name = 'se.prescription.plan'
    _description = "Prescription Plan"

    name = fields.Char('Name')

    
class SePrescriptionDisease(models.Model):
    _name = 'se.prescription.disease'
    _description = "Prescription Disease"

    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Text('Description')
    clasification = fields.Selection([ ('acute', 'Acute'), ('chronic', 'Chronic'), ('infectious', 'Infectious'), ('non_infectious', 'Non Infectious')], 'Clasification')
    is_active = fields.Boolean('Active', default=True)
    catagory = fields.Selection([ ('internal', 'Internal'), ('external', 'External')], 'Catagory')
    prescription_order_id = fields.Many2one('se.prescription.order', string='Prescription Order')
    
    
class SePrescriptionLabTest(models.Model):
    _name = 'se.prescription.lab.test'
    _description = "Prescription Lab Test"

    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Text('Description')
    is_active = fields.Boolean('Active', default=True)
    
    
class SeHealthDocotrsSpecializationBangla(models.Model):
    _name = 'se.health.docotrs.specialization.bangla'
    _description = "Doctors Specialization"

    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Text('Description')
    is_active = fields.Boolean('Active', default=True)
    
class SeHealthDocotrsDegreeBangla(models.Model):
    _name = 'se.health.docotrs.degree.bangla'
    _description = "Doctors Degree"

    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Text('Description')
    is_active = fields.Boolean('Active', default=True)
    
    
class SeHealthDocDepartments(models.Model):
    _name = 'se.health.doc.departments'
    _description = "Doctors Departments"

    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Text('Description')
    is_active = fields.Boolean('Active', default=True)
    