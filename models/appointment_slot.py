from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime


class SeAppointmentSlots(models.Model):
    _name = 'se.appointment.slots'
    _description = "Appointment Slots"

    name = fields.Char('Name')
    doctor_id = fields.Many2one(
        'res.partner', 
        string='Doctor', 
        required=True, 
        domain=[('partner_type', '=', 'doctor')]
    )
    duration_per_slot = fields.Float('Duration per Slot (in minutes)', required=True)
    work_from = fields.Float('Work From (in hours)', required=True, help="Enter time in hours, e.g., 9.0 for 9:00 AM")
    work_to = fields.Float('Work To (in hours)', required=True, help="Enter time in hours, e.g., 17.5 for 5:30 PM")
    
    slot_line_ids = fields.One2many('se.appointment.slots.line', 'slot_id',ondelete='cascade', string='Slot Lines')
    date = fields.Date('Slot From', required=True, default=fields.Date.today)
    slot_to_date = fields.Date('Slot To', required=True)

    @api.constrains('duration_per_slot', 'work_from', 'work_to')
    def _check_duration_and_time(self):
        """Ensure the slot duration is a positive value and the working hours are valid."""
        for record in self:
            if record.duration_per_slot <= 0:
                raise UserError(_("Duration per slot must be a positive value."))
            if record.work_from >= record.work_to:
                raise UserError(_("Work To time must be after Work From time."))

    def generate_slots(self):
        """Generate slots based on the work hours, duration per slot, and date range."""
        if not self.duration_per_slot:
            raise UserError(_("Please set the duration per slot."))
        if self.date > self.slot_to_date:
            raise UserError(_("Slot From date cannot be after Slot To date."))

        # Prepare working hours
        work_from_in_seconds = int(self.work_from * 3600)  # Convert work_from hours to seconds
        work_to_in_seconds = int(self.work_to * 3600)      # Convert work_to hours to seconds
        work_duration_in_seconds = work_to_in_seconds - work_from_in_seconds

        # Validate if work_to is after work_from
        if work_duration_in_seconds <= 0:
            raise UserError(_("Work To must be after Work From."))

        # Calculate number of slots per day
        slots_per_day = work_duration_in_seconds / (self.duration_per_slot * 60)

        # Generate slots for each day between slot_from and slot_to_date
        slot_lines = []
        current_date = self.date
        while current_date <= self.slot_to_date:
            current_time_in_seconds = work_from_in_seconds
            for i in range(int(slots_per_day)):
                # Calculate the start and end times for each slot
                slot_start_time = (datetime.combine(current_date, datetime.min.time()) + timedelta(seconds=current_time_in_seconds)).time()
                slot_end_time = (datetime.combine(current_date, datetime.min.time()) + timedelta(seconds=current_time_in_seconds + self.duration_per_slot * 60)).time()

                # Format slot name as "Doctor Name: HH:MM-HH:MM (YYYY-MM-DD)"
                slot_name = f"{self.doctor_id.name}: {slot_start_time.strftime('%H:%M')}-{slot_end_time.strftime('%H:%M')} ({current_date.strftime('%Y-%m-%d')})"
                
                # Append slot line
                slot_lines.append((0, 0, {
                    'name': slot_name,
                    'date': current_date,
                    'is_available': True,
                    'slot_id': self.id,
                    'doctor_id': self.doctor_id.id,
                }))
                
                # Move to the next time slot
                current_time_in_seconds += int(self.duration_per_slot * 60)

            # Move to the next day
            current_date += timedelta(days=1)

        # Assign generated slots
        self.slot_line_ids = slot_lines
        return True


class SeAppointmentSlotsLine(models.Model):
    _name = 'se.appointment.slots.line'
    _description = "Appointment Slots Line"

    name = fields.Char('Slot')
    slot_id = fields.Many2one('se.appointment.slots', string='Slot', required=True, ondelete='cascade')
    is_available = fields.Boolean('Available', default=True)
    cabin_id = fields.Many2one('se.health.consultation.room', string='Cabin')
    date = fields.Date('Date')
    doctor_id = fields.Many2one('res.partner', string='Doctor', related='slot_id.doctor_id', store=True)
    department_id = fields.Many2one('se.health.doc.departments', string='Department', related='doctor_id.doc_dept_id', store=True)
