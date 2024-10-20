# -- coding: utf-8 --
from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class SeAppoinement(models.Model):
    _name = 'se.health.appoinement'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, default='New Appointment')
    active = fields.Boolean(string='Active', default=True)
    patient_id = fields.Many2one('res.partner', string='Name', required=True, tracking=True, domain="[('partner_type', '=', patient_type)]")
    patient_type = fields.Selection(
        [
            ('student', 'Student'),
            ('staff', 'Staff'),
            ('faculty', 'Faculty'),
            ('alumni', 'Alumni'),
            ('other', 'Other'),
        ],
        string='Patient Type',
        tracking=True
    )
    dob = fields.Date(string='Date of Birth', related='patient_id.date_of_birth', store=True)
    patient_age = fields.Integer(string='Age',tracking=True)
    doctor_id = fields.Many2one(
        'res.partner', 
        string='Doctor', 
        required=True,tracking=True,
        domain=[('partner_type', '=', 'doctor')]
    )
    # appointment_to = fields.Datetime(string='Appointment To', required=True,tracking=True)
    video_call_url = fields.Char(string='Video Call URL',tracking=True)
    note = fields.Text(string='Note',tracking=True)
    cabin_id = fields.Many2one('se.health.consultation.room', string='Consultation Room',tracking=True)
    date = fields.Date(string='Date', default=fields.Date.today,tracking=True) 
    urgency_level = fields.Selection([('not_urgent','Not Urgent'),('normal', 'Normal'), ('medium', 'Medium'), ('high', 'High')],
                                    string='Urgency Level', default='normal',tracking=True)
    chief_complaint = fields.Text(string='Chief Complaint',tracking=True)
    history_of_present_illness = fields.Text(string='History of Present Illness',tracking=True)
    past_history = fields.Text(string='Past History',tracking=True)
    family_history = fields.Text(string='Family History',tracking=True)
    
    
    appointment_type = fields.Selection([('clinic', 'Clinic'), ('home', 'Home'), ('online', 'Online')],
                                        string='Appointment Type', default='clinic',tracking=True)
    appointment_reason = fields.Selection([('consultation', 'Consultation'), ('followup', 'Follow Up'), ('checkup', 'Check Up')],
                                        string='Appointment Reason', default='consultation',tracking=True)
    
    blood_group = fields.Selection(
        [
            ('A+', 'A+ve'),
            ('B+', 'B+ve'),
            ('O+', 'O+ve'),
            ('AB+', 'AB+ve'),
            ('A-', 'A-ve'),
            ('B-', 'B-ve'),
            ('O-', 'O-ve'),
            ('AB-', 'AB-ve'),
        ],
        string='Blood Group',
        tracking=True
    )
    # slots of selected doctor and available
    slot_line_id = fields.Many2one('se.appointment.slots.line', string='Slot',tracking=True, ondelete='cascade',domain="[('doctor_id', '=', doctor_id), ('is_available', '=', True)]")

    systolic_bp = fields.Integer(string='Systolic BP',tracking=True, readonly=True)
    diastolic_bp = fields.Integer(string='Diastolic BP',tracking=True, readonly=True)
    weight = fields.Float(string='Weight(in kg)',tracking=True, readonly=True)
    height = fields.Float(string='Height(in cm)',tracking=True, readonly=True)
    temperature = fields.Float(string='Temperature(in F)',tracking=True, readonly=True)
    pulse = fields.Float(string='Pulse(per minute)',tracking=True, readonly=True)
    bmi = fields.Float('BMI',tracking=True, readonly=True)
    bmi_state = fields.Selection(
        [('underweight', 'Underweight'), ('normal', 'Normal'), ('overweight', 'Overweight'), ('obese', 'Obese')],
        string='BMI State',tracking=True, readonly=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('waiting', 'Waiting'),
        ('in_consultation', 'In Consultation'),
        ('pause', 'Pause'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        # Create the appointment
        appointment = super(SeAppoinement, self).create(vals)
        
        # Set the slot to unavailable once it has been selected
        if appointment.slot_line_id:
            appointment.slot_line_id.is_available = False
        
        return appointment

    def write(self, vals):
        res = super(SeAppoinement, self).write(vals)
        
        # If slot_line_id is updated, set the new slot to unavailable
        if 'slot_line_id' in vals and self.slot_line_id:
            self.slot_line_id.is_available = False
        
        return res
    
    def action_create_evaluation(self):
        # Create an evaluation and open the form view for it
        evaluation = self.env['se.patient.evaluation'].create({
            'appointment_id': self.id,
            'weight': self.weight,
            'height': self.height,
            'temperature': self.temperature,
            'pulse': self.pulse,
            'systolic_bp': self.systolic_bp,
            'diastolic_bp': self.diastolic_bp,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Evaluation',
            'res_model': 'se.patient.evaluation',
            'view_mode': 'form',
            # 'res_id': evaluation.id,
            'target': 'new',
            'context': {'default_appointment_id': self.id}
        }



    def action_start_consultation(self):
        # Confirm -> In Consultation state
        # self.ensure_one()
        # if self.state != 'confirm':
        #     raise UserError("Cannot start consultation unless the state is 'Confirmed'.")
        self.state = 'in_consultation'
        # self.message_post(body="Consultation started.")

    def action_pause_consultation(self):
        # In Consultation -> Pause state
        self.ensure_one()
        if self.state != 'in_consultation':
            raise UserError("Cannot pause unless the consultation is in progress.")
        self.state = 'pause'
        # self.message_post(body="Consultation paused.")

    def action_done_consultation(self):
        # In Consultation -> Done state
        self.ensure_one()
        if self.state != 'in_consultation':
            raise UserError("Cannot mark as done unless the consultation is in progress.")
        self.state = 'done'
        # self.message_post(body="Consultation marked as done. No further actions allowed.")

    def action_resume_consultation(self):
        # Pause -> In Consultation state
        self.ensure_one()
        if self.state != 'pause':
            raise UserError("Can only resume if the consultation is paused.")
        self.state = 'in_consultation'
        # self.message_post(body="Consultation resumed.")

    def action_reset(self):
        # Reset to Draft state
        self.ensure_one()
        self.state = 'draft'
        # self.message_post(body="Appointment reset to draft.")

    def action_cancel(self):
        # Change state to Cancelled
        self.ensure_one()
        if self.state in ['done', 'cancel']:
            raise UserError("Cannot cancel a done or already cancelled appointment.")
        self.state = 'cancel'
        # self.message_post(body="Appointment cancelled.")

    def action_waiting(self):
        # Confirm -> Waiting state
        self.state = 'waiting'
        # self.message_post(body="Appointment set to In consultation.")

    def action_confirm(self):
        # Draft -> Confirm state
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Can only confirm from draft state.")
        self.state = 'confirm'
        # self.message_post(body="Appointment confirmed.")
    
    def action_view_invoices(self):
        """Show only invoices related to the 'Health Appointment Fees' product."""
        self.ensure_one()

        # Get the service product 'Health Appointment Fees'
        service_product = self.env.ref('mini_clinic.product_product_health_appointment_fees_product')
        if not service_product:
            raise UserError(_("Product 'Health Appointment Fees' not found. Please ensure it is configured."))

        # Get all invoices for the current patient that include the 'Health Appointment Fees' product
        invoices = self.env['account.move'].search([
            ('partner_id', '=', self.patient_id.id),
            ('move_type', '=', 'out_invoice'),
            ('invoice_line_ids.product_id', '=', service_product.id),
        ])

        # Return an action to show the filtered invoices
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', invoices.ids)],
            'target': 'current',
        }

        
    def action_view_prescriptions(self):
        self.ensure_one()
        # Get all prescriptions for the current patient
        prescriptions = self.env['se.prescription.order'].search([('patient_id', '=', self.patient_id.id), ('appointment_id', '=', self.id)])
        
        return {
            'name': 'Prescriptions',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'se.prescription.order',
            'domain': [('id', 'in', prescriptions.ids)],
            'target': 'current',
        }
        
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            # Fetch the patient from res.partner (which is inherited by Student)
            patient = self.env['res.partner'].search([('id', '=', self.patient_id.id)], limit=1)
            if patient:
                # Set blood group from patient record if available (assuming it's a field in res.partner)
                self.blood_group = patient.blood_group if hasattr(patient, 'blood_group') else False
                
                # Calculate patient age from date_of_birth
                if patient.date_of_birth:
                    today = date.today()
                    born = patient.date_of_birth
                    self.patient_age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                else:
                    self.patient_age = False
            else:
                self.blood_group = False
                self.patient_age = False
    
    
    def action_create_invoice(self):
        self.ensure_one()

        service_product = self.env.ref('mini_clinic.product_product_health_appointment_fees_product')
        if not service_product:
            raise UserError(_("Please configure/Create a product named 'Health Appointment Fees' for invoicing."))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.patient_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': [(0, 0, {
                'product_id': service_product.id,
                'quantity': 1.0,  # Always 1 quantity
                'price_unit': service_product.lst_price,
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)

        invoice.action_post()


        # self.message_post(body=_("Invoice created and posted: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (invoice.id, invoice.name))

        return invoice
    



    def button_prescription_order(self):
        """Open Prescription Order Form View and Create or Edit Prescription."""
        if self.state != 'in_consultation':
            raise UserError(_("You can  only create an Prescription in Consultation state."))
        # self.write({'state': 'end'})
        action = self.env["ir.actions.actions"]._for_xml_id("mini_clinic.action_se_prescription_order")
        action['domain'] = [('appointment_id', '=', self.id)]
        action['views'] = [(self.env.ref('mini_clinic.view_se_prescription_order_form').id, 'form')]
        action['context'] = {
            'default_patient_id': self.patient_id.id,
            'default_doctor_id': self.doctor_id.id,
            'default_appointment_id': self.id,  # Corrected from self.name.id to self.id
        }
        return action


    # @api.onchange('appointment_from', 'appointment_to')
    # def _onchange_compute_duration(self):
    #     """Calculate the duration in minutes between appointment_from and appointment_to."""
    #     for record in self:
    #         if record.appointment_from and record.appointment_to:
    #             duration = (record.appointment_to - record.appointment_from).total_seconds() / 60.0
    #             record.duration = duration
    #         else:
    #             record.duration = 0.0

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('se.health.appoinement') 
        return super(SeAppoinement, self).create(vals)
            
    

class SeHealthConsultationRoom(models.Model):
    _name = 'se.health.consultation.room'
    _description = 'Consultation Room'
    _order = "id desc"

    name = fields.Char(string='Name', required=True, copy=False)
    room_number = fields.Char(string='Room Number', required=True)
    capacity = fields.Integer(string='Capacity', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    
    
    
class SePatientEvaluation(models.TransientModel):
    _name = 'se.patient.evaluation'
    _description = 'Patient Evaluation'
    _order = "id desc"

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, default='New Evaluation')
    appointment_id = fields.Many2one('se.health.appoinement', string='Appointment', required=True)
    weight = fields.Float(string='Weight(in kg)')
    height = fields.Float(string='Height(in cm)')
    temperature = fields.Float(string='Temperature(in F)')
    pulse = fields.Float(string='Pulse(per minute)')
    systolic_bp = fields.Integer("Systolic BP")
    diastolic_bp = fields.Integer("Diastolic BP")
    bmi_state = fields.Selection([('underweight', 'Underweight'), ('normal', 'Normal'), ('overweight', 'Overweight'), ('obese', 'Obese')],
                                 string='BMI State', compute='_compute_bmi_state')
    bmi = fields.Float('BMI', compute='_compute_bmi')

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for record in self:
            if record.weight and record.height:
                record.bmi = record.weight / ((record.height / 100) ** 2)
            else:
                record.bmi = 0.0

    @api.depends('bmi')
    def _compute_bmi_state(self):
        for record in self:
            if record.bmi < 18.5:
                record.bmi_state = 'underweight'
            elif 18.5 <= record.bmi < 25:
                record.bmi_state = 'normal'
            elif 25 <= record.bmi < 30:
                record.bmi_state = 'overweight'
            else:
                record.bmi_state = 'obese'
    @api.model
    def create(self, vals):
        # Create the patient evaluation record
        evaluation = super(SePatientEvaluation, self).create(vals)
        
        # After creating the evaluation, update the corresponding appointment with the evaluation data
        if evaluation.appointment_id:
            evaluation.appointment_id.write({
                'systolic_bp': evaluation.systolic_bp,
                'diastolic_bp': evaluation.diastolic_bp,
                'weight': evaluation.weight,
                'height': evaluation.height,
                'temperature': evaluation.temperature,
                'pulse': evaluation.pulse,
                'bmi': evaluation.bmi,
                'bmi_state': evaluation.bmi_state,
            })
        
        return evaluation
