import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
# comment

class ProjectTask(models.Model):
    _inherit = 'project.task'

    visit_sequence = fields.Integer(string="Visit Sequence", default=0, readonly=True)
    travel_duration = fields.Float(string="Travel Duration (Hours)", help="Estimated travel time to this location")
    
    intervention_duration = fields.Float(string="Intervention Duration (Hours)", default=1.0, help="Expected time spent on the task")
    estimated_arrival = fields.Datetime(string="Estimated Arrival", readonly=True, help="Calculated arrival time based on route optimization")
    partner_city = fields.Char(related='partner_id.city', string="City", store=True, readonly=True)
    
    route_id = fields.Many2one('field.service.route', string="Route", ondelete='set null')
