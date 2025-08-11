from odoo import models, fields

class NrcTownship(models.Model):
    _name = 'nrc.township'
    _description = 'NRC Township'
    _rec_name = 'code'

    name = fields.Char(required=True, string="Township Code")
    code = fields.Char(required=True)
    state_code = fields.Selection([
        ('၁', '၁'), ('၂', '၂'),
        ('၃', '၃'), ('၄', '၄'),
        ('၅', '၅'), ('၆', '၆'),
        ('၇', '၇'), ('၈', '၈'),
        ('၉', '၉'), ('၁၀', '၁၀'),
        ('၁၁', '၁၁'), ('၁၂', '၁၂'),
        ('၁၃', '၁၃'), ('၁၄', '၁၄'),
    ], string="State Code")
