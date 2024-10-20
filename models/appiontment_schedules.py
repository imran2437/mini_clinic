# -- coding: utf-8 --
from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SeAppoinementSchedules(models.Model):
    _name = 'se.appoinement.schedules'
    _description = "Appoinement Schedules"

    name = fields.Char('Name')
    doctor_id = fields.Many2one(
        'res.partner', 
        string='Doctor', 
        required=True,tracking=True,
        domain=[('partner_type', '=', 'doctor')]
    )
    active = fields.Boolean('Active', default=True)
    schedule_line_ids = fields.One2many('se.appoinement.schedules.line', 'schedule_id', string='Schedule Lines')
    timezone = fields.Selection([ ('utc', 'UTC'), ('gmt', 'GMT'), ('est', 'EST'), ('cst', 'CST'), ('mst', 'MST'), ('pst', 'PST')], 'Timezone')
    
    
class SeAppoinementSchedulesLine(models.Model):
    _name = 'se.appoinement.schedules.line'
    _description = "Appoinement Schedules Line"

    name = fields.Char('Name')
    is_active = fields.Boolean('Active', default=True)  
    schedule_id = fields.Many2one('se.appoinement.schedules', string='Schedule')
    day = fields.Selection([ ('sunday', 'Sunday'), ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday')], 'Day')
    work_from = fields.Datetime('Work From')
    work_to = fields.Datetime('Work To')
    workin_hours = fields.Float('Working Hours')
    
    @api.onchange('work_from', 'work_to')
    def _onchange_start_work_to(self):
        if self.work_from and self.work_to:
            if self.work_from > self.work_to:
                raise UserError(_('Work To cannot be set before work from.'))
            self.workin_hours = (self.work_to - self.work_from).seconds / 3600.0
        else:
            self.workin_hours = 0.0
            