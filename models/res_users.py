from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    default_start_address_id = fields.Many2one(
        'res.partner',
        string="Default Start Address",
        help="The starting point for route optimization (e.g., Home or Depot)."
    )
