from odoo import models, fields

class DaySelection(models.Model):
    _name = 'day.selection'
    _description = 'Day Selection'

    name = fields.Char(string='Day Name', required=True)

    
