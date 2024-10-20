# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import uuid


class SePrescriptionOrder(models.Model):
    _name='se.prescription.order'
    _description = "Prescription Order"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Prescriptuion ID', required=True, copy=False, readonly=True, default='New Prescription')
    active = fields.Boolean('Active' , default=True)
    code = fields.Char('Code')
    note = fields.Text('Note')
    patient_id = fields.Many2one('res.partner', string='Patient', required=True)
    # releted field age
    patient_age = fields.Integer(related='appointment_id.patient_age', string='Age', store=True)
    doctor_id = fields.Many2one(
    'res.partner', 
    string='Doctor', 
    required=True,
    domain=[('partner_type', '=', 'doctor')]
    )
    prescription_date = fields.Date('Prescription Date', default=fields.Datetime.now, tracking=True , required=True)
    prescription_suggestions = fields.Many2many('se.prescription.suggestions', string='Suggestions')
    prescription_diagnosis = fields.Many2many('se.prescription.diagnosis', string='Diagnosis')
    prescription_plan = fields.Many2many('se.prescription.plan', string='Plan')
    next_followup_date = fields.Date('Next Followup Date')
    prescription_disease = fields.Many2many('se.prescription.disease', string='Disease')
    prescription_instruction = fields.Text('Instruction')
    medicine = fields.One2many('se.prescription.line', 'prescription_id', string='Medicine')
    appointment_id = fields.Many2one('se.health.appoinement', string='Appointment Id')
    lab_test_ids = fields.Many2many('se.prescription.lab.test', string='Lab Tests')
    
    state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Prescribed'),
    ('sent', 'Sent by Email'),
    ('invoiced', 'Invoiced')
    ], string='Status', default='draft', tracking=True)
    
    prescription_template_id = fields.Many2one('se.prescription.template', string='Prescription Template')
    last_prescription_id = fields.Many2one(
        'se.prescription.order', 
        string='Old Prescription',
        domain="[('patient_id', '=', patient_id), ('id', '!=', id)]",  # Show only prescriptions for the selected patient except the current one
        readonly=False
    )
    
    @api.onchange('patient_id')
    def _onchange_patient(self):
        """Auto-select the last prescription for the selected patient."""
        if self.patient_id:
            domain = [('patient_id', '=', self.patient_id.id), ('state', '=', 'confirmed')]
            
            # Check if the current record is already saved (not a temporary record)
            if self.id:
                domain.append(('id', '!=', self.id))

            last_prescription = self.env['se.prescription.order'].search(domain, order='prescription_date desc', limit=1)

            if last_prescription:
                self.last_prescription_id = last_prescription.id

    

    @api.model
    def create(self, vals):
        if vals.get('name', 'New Prescription') == 'New Prescription':
            vals['name'] = self.env['ir.sequence'].next_by_code('se.prescription.order') or 'New Prescription'
        return super(SePrescriptionOrder, self).create(vals)
        
    @api.onchange('prescription_template_id')
    def _onchange_prescription_template(self):
        if self.prescription_template_id:
            template = self.prescription_template_id
            
            # Auto-fill fields based on the selected template
            self.doctor_id = template.doctor_id.id
            self.prescription_disease = template.disease_ids.ids
            self.prescription_suggestions = template.suggestions_ids.ids
            self.prescription_diagnosis = template.diagnosis_ids.ids
            self.prescription_plan = template.plan_ids.ids
            self.lab_test_ids = template.lab_test_ids.ids

            # Auto-fill medicines
            self.medicine = [(5, 0, 0)]  # Clear existing medicines
            for medicine in template.medicine_ids:
                self.medicine = [(0, 0, {
                    'product_id': medicine.product_id.id,
                    'quantity': medicine.quantity,
                    'dose': medicine.dose,
                    'days': medicine.days,
                    'qty_per_day': medicine.qty_per_day,
                    'dose_suggestions': medicine.dose_suggestions.id
                })]
                
    
    def action_send_email(self):
        """Sends an email with the prescription order and logs it in the chatter."""
        self.ensure_one()

        # Get the email template
        template = self.env.ref('mini_clinic.email_template_prescription_order', raise_if_not_found=False)

        if template:
            # Send the email
            template.send_mail(self.id, force_send=True)

            # Log the email action in the chatter
            self.message_post(body=_("Prescription email sent using template: <a href=# data-oe-model=mail.template data-oe-id=%d>%s</a>") % (template.id, template.name))

        # Update the state to 'sent'
        self.write({'state': 'sent'})

        return True

    
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
        
    def action_create_invoice(self):
        if self.state != 'draft':
            raise UserError(_("You can only create an invoice  in the draft state."))
        invoice_obj = self.env['account.move']
        stock_picking_obj = self.env['stock.picking']
        self.write({'state': 'invoiced'})
        for order in self:
            if not order.medicine:
                raise UserError(_("Cannot create an invoice without medicines in the prescription."))

            # Create delivery order for reducing stock
            picking_type_id = self.env.ref('stock.picking_type_out').id
            picking = stock_picking_obj.create({
                'partner_id': order.patient_id.id,
                'picking_type_id': picking_type_id,
                'origin': order.name,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                'move_ids_without_package': [(0, 0, {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                }) for line in order.medicine],
            })

            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()

            # Create invoice
            invoice_lines = []
            for line in order.medicine:
                invoice_lines.append((0, 0, {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.product_id.list_price,
                    'tax_ids': [(6, 0, line.product_id.taxes_id.ids)],
                    'account_id': line.product_id.categ_id.property_account_income_categ_id.id or self.env['ir.property']._get('property_account_income_categ_id', 'product.category').id,
                }))

            invoice = invoice_obj.create({
                'move_type': 'out_invoice',
                'partner_id': order.patient_id.id,
                'invoice_origin': order.name,
                'invoice_date': fields.Date.context_today(self),
                'invoice_line_ids': invoice_lines,
            })

            order.write({'state': 'invoiced'})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoice.id,
                'view_id': self.env.ref('account.view_move_form').id,
            }

    
        
    class SePrescriptionLine(models.Model):
        _name = 'se.prescription.line'
        _description = "Prescription Order Line" 

        name = fields.Char()
        prescription_id = fields.Many2one('se.prescription.order', string='Prescription')
        product_id = fields.Many2one('product.product', string='Medicine', domain=[('is_medicine', '=', 'true')])
        allow_substitution = fields.Boolean(string='Allow Substitution')
        quantity = fields.Float(string='Units', help="Number of units of the medicament. Example : 30 capsules of amoxicillin",default=1.0)
        manual_quantity = fields.Float(string='Manual Total Qty', default=1)
        dose = fields.Float('Dosage(mg)', help="Amount of medication (eg, 250 mg) per dose",default=1.0)
        short_comment = fields.Char(string='Comment', help='Short comment on the specific drug')
        qty_available = fields.Float( string='Available Qty')
        days = fields.Float("Days",default=1.0)
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
        days_in_bangla=fields.Char(string='Days in Bangla',default='১')
        coment = fields.Char(string='Comment')
        
        
    class SePrescriptionDoseSuggestions(models.Model):
        _name = 'se.prescription.dose.suggestions'
        _description = "Prescription Dose Suggestions"
        
        name = fields.Char('Dose Suggestions')
        description = fields.Text('Description')
    
