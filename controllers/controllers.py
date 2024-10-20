from odoo import http, fields
from odoo.http import request

class HealthPortal(http.Controller):

    # Route to show previous prescriptions
    @http.route(['/my/appointments'], type='http', auth="user", website=True)
    def portal_my_appointments(self):
        partner = request.env.user.partner_id

        # Get previous prescriptions for the logged-in user
        prescriptions = request.env['se.prescription.order'].search([
            ('patient_id', '=', partner.id)
        ])

        return request.render('mini_clinic.portal_appointment_prescriptions', {
            'prescriptions': prescriptions
        })

    # Route to request a new appointment
    @http.route(['/my/appointments/request'], type='http', auth="user", website=True, methods=['GET', 'POST'], csrf=True)
    def portal_request_appointment(self, **post):
        # Get list of doctors
        doctors = request.env['res.partner'].search([('partner_type', '=', 'doctor')])

        slots = []
        selected_doctor = post.get('doctor_id')
        if selected_doctor:
            slots = request.env['se.appointment.slots.line'].search([
                ('is_available', '=', True),
                ('doctor_id', '=', int(selected_doctor)),
                ('date', '>=', fields.Date.today())
            ])

        if request.httprequest.method == 'POST':
            # Handle form submission
            partner = request.env.user.partner_id
            doctor_id = post.get('doctor_id')
            slot_id = post.get('slot_id')  # Add the slot selection here
            urgency_level = post.get('urgency_level')
            chief_complaint = post.get('chief_complaint')

            # Validate form data
            if not doctor_id or not slot_id or not urgency_level or not chief_complaint:
                return request.redirect('/my/appointments/request?error=missing_data')

            # Create appointment
            request.env['se.health.appoinement'].create({
                'patient_id': partner.id,
                'doctor_id': int(doctor_id),
                'slot_line_id': int(slot_id),  # Store the selected slot
                'urgency_level': urgency_level,
                'chief_complaint': chief_complaint,
                'state': 'draft',
            })

            # Mark the selected slot as unavailable
            slot = request.env['se.appointment.slots.line'].browse(int(slot_id))
            slot.is_available = False

            return request.redirect('/my/appointments?success=true')

        return request.render('mini_clinic.portal_request_appointment', {
            'doctors': doctors,
            'slots': slots,
            'selected_doctor': selected_doctor,
            'selected_slot': post.get('slot_id'),
        })

    # AJAX route to fetch slots based on selected doctor   
    @http.route('/get_slots', type='http', auth="public", methods=['GET'])
    def get_slots(self, doctor_id=None):
        if doctor_id:
            slots = request.env['se.appointment.slots.line'].sudo().search([
                ('doctor_id', '=', int(doctor_id)),
                ('is_available', '=', True),
                ('date', '>=', fields.Date.today())
            ])  
            output = ''
            if not slots:
                output += '<p>No available slots found</p>'
            else:
                for slot in slots:
                    output += ' <option value="{}">{}</option>'.format(slot.id, slot.name)
            return request.make_response(output, headers={'Content-Type': 'text/html'})

        return request.make_response('<p>No doctor selected</p>', headers={'Content-Type': 'text/html'})


    
    # Route to handle requested appointments
    @http.route(['/my/appointments/requests'], type='http', auth="user", website=True)
    def portal_my_requested_appointments(self):
        partner = request.env.user.partner_id

        # Get all requested appointments for the logged-in user
        appointments = request.env['se.health.appoinement'].search([
            ('patient_id', '=', partner.id)
        ])

        return request.render('mini_clinic.portal_requested_appointments', {
            'appointments': appointments
        })