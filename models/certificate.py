from odoo import models, fields

class Certification(models.Model):
    _name = "certification"
    _description = "Certification"

    name = fields.Char(string="Certification Name", required=True)
