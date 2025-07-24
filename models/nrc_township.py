from odoo import models, fields

class NrcTownship(models.Model):
    _name = 'nrc.township'
    _description = 'NRC Township'
    _rec_name = 'code'

    name = fields.Char(required=True, string="Township Code")
    code = fields.Char(required=True)
    state_code = fields.Selection([
        ('1', '1'), ('2', '2'),
        ('3', '3'), ('4', '4'),
        ('5', '5'), ('6', '6'),
        ('7', '7'), ('8', '8'),
        ('9', '9'), ('10', '10'),
        ('11', '11'), ('12', '12'),
        ('13', '1'), ('14', '14'),
    ], string="State Code")
