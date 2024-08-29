from odoo import models, fields, api

class ProductMarginReportTag(models.Model):
    _name = 'margin.tag'
    _description = "To categorize product"

    name = fields.Char(string='Category Name', required=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text(string='Description')  