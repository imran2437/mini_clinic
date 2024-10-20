# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging
from odoo.exceptions import ValidationError
from datetime import date
import re
from datetime import datetime, date,timedelta


class Dashboard(models.Model):
    _name = 'se.health.dashboard'
    _description = 'Dashboard'

    name = fields.Char(string='Name', default='Dashboard')
    total_doctors = fields.Integer(string='Total Doctors', compute='_compute_total_doctors')
    total_patients = fields.Integer(string='Total Patients', compute='_compute_total_patients')
    total_appointments = fields.Integer(string='Total Appointments', compute='_compute_total_appointments')
    appoinement_today = fields.Integer(string='Today Appointments', compute='_compute_appoinement_today')
    referred_draft_appointments = fields.Integer(string="Referred Draft Appointments", compute='_compute_referred_draft_appointments')

    @api.depends()
    def _compute_referred_draft_appointments(self):
        user = self.env.user
        for record in self:
            if user.partner_id.partner_type == 'doctor':
                record.referred_draft_appointments = self.env['se.health.appoinement'].search_count([
                    ('doctor_id', '=', user.partner_id.id),
                    ('state', '=', 'draft')
                ])
            else:
                record.referred_draft_appointments = 0

    def action_view_referred_draft_appointments(self):
        self.ensure_one()
        user = self.env.user
        action = {}
        if user.partner_id.partner_type == 'doctor':
            action = {
                'name': _('Referred Draft Appointments'),
                'view_mode': 'tree,form',
                'res_model': 'se.health.appoinement',
                'type': 'ir.actions.act_window',
                'context': {},
                'domain': [
                    ('doctor_id', '=', user.partner_id.id),
                    ('state', '=', 'draft')
                ],
                'help': _('Click to view referred draft appointments.'),
            }
        return action

    @api.depends()
    def _compute_total_doctors(self):
        for record in self:
            record.total_doctors = self.env['res.partner'].search_count([('partner_type', '=', 'doctor')])

    @api.depends()
    def _compute_total_patients(self):
        for record in self:
            record.total_patients = self.env['res.partner'].search_count([])
            
    @api.depends()
    def _compute_total_appointments(self):
        for record in self:
            record.total_appointments = self.env['se.health.appoinement'].search_count([])
            
    @api.depends()
    def _compute_appoinement_today(self):
        today = date.today()
        for record in self:
            record.appoinement_today = self.env['se.health.appoinement'].search_count([
                ('date', '>=', today),
                ('date', '<', today + timedelta(days=1))
            ])
                
    def action_view_doctors(self):
        self.ensure_one()
        action = {
            'name': _('Doctors'),
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'context': {},
            'domain': [('partner_type', '=', 'doctor')],
            'help': _('Click to view doctors.'),
        }
        return action
    
    def action_view_patients(self):
        self.ensure_one()
        action = {
            'name': _('Patients'),
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'context': {},
            'help': _('Click to view patients.'),
        }
        return action

    def action_view_appointments(self):
        self.ensure_one()
        action = {
            'name': _('Appointments'),
            'view_mode': 'tree,form',
            'res_model': 'se.health.appoinement',
            'type': 'ir.actions.act_window',
            'context': {},
            'domain': [],
            'help': _('Click to view appointments.'),
        }
        return action
    
    
    def action_view_appointments_today(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        action = {
            'name': _('Today Appointments'),
            'view_mode': 'tree,form',
            'res_model': 'se.health.appoinement',
            'type': 'ir.actions.act_window',
            'context': {},
            'domain': [
                ('date', '>=', today),
                ('date', '<', today + timedelta(days=1))
            ],
            'help': _('Click to view today\'s appointments.'),
        }
        return action

    
    