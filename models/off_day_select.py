from odoo import models, fields

class DaySelection(models.Model):
    _name = 'day.selection'
    _description = 'Day Selection'
    _rec_name = 'name'

    name = fields.Char(string='Day Name', required=True)

    
