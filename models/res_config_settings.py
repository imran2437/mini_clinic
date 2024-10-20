from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    def _default_health_appointment_fees_product_id(self):
        try:
            res = self.env.ref('mini_clinic.product_product_health_appointment_fees_product', raise_if_not_found=False)
            return res.id if res else False
        except ValueError:
            return False


    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id.id, readonly=True)
    health_appointment_fees = fields.Float(string='Health Appointment Fees', default=0, config_parameter='mini_clinic.health_appointment_fees')
    health_appointment_fees_product_id = fields.Many2one(comodel_name='product.product', string='Health Appointment Fees Product', config_parameter='mini_clinic.health_appointment_fees_product_id', default=_default_health_appointment_fees_product_id)
