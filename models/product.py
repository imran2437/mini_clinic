# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class product_template(models.Model):
    _inherit = "product.template"

    # hospital_product_type = fields.Selection([
    #     ('medicament','Medicament'),
    #     ('fdrinks', 'Food & Drinks'),
    #     ('os', 'Other Service'),
    #     ('not_medical', 'Not Medical'),], string="Hospital Product Type")
    is_medicine = fields.Boolean(string="Is Medicine")
