import logging
from math import radians, cos, sin, asin, sqrt
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class RouteOptimizerWizard(models.TransientModel):
    _name = 'field.service.route.optimizer.wizard'
    _description = 'Route Optimization Wizard'

    start_datetime = fields.Datetime(string="Start Date & Time", required=True, default=fields.Datetime.now)
    task_ids = fields.Many2many('project.task', string="Tasks to Optimize")

    def _get_coordinates(self, partner):
        """Helper to return coords or raise error"""
        if not partner or not partner.partner_latitude or not partner.partner_longitude:
            return None
        return (partner.partner_latitude, partner.partner_longitude)

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees) in Kilometers.
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers.
        return c * r

    def action_optimize(self):
        """
        Optimizes the route for the selected tasks.
        """
        self.ensure_one()
        tasks = self.task_ids
        if not tasks:
            raise UserError(_("No tasks selected for optimization."))

        user_start_partner = self.env.user.default_start_address_id
        if not user_start_partner:
            raise UserError(_("Please configure a Default Start Address in your User Preferences."))

        start_coords = self._get_coordinates(user_start_partner)
        if not start_coords:
            raise UserError(_("The Start Address (Partner: %s) does not have valid Geolocation.") % user_start_partner.name)

        # Filter tasks that have valid partners with coordinates
        locations = []
        for task in tasks:
            coords = self._get_coordinates(task.partner_id)
            if not coords:
                raise UserError(_("Task '%s' (Customer: %s) is missing Geolocation coordinates.") % (task.name, task.partner_id.name))
            locations.append({
                'task': task,
                'lat': coords[0],
                'lon': coords[1],
                'visited': False
            })

        # 2. Optimization Algorithm (Nearest Neighbor)
        current_lat = start_coords[0]
        current_lon = start_coords[1]
        
        sequence_counter = 1
        current_time = self.start_datetime
        
        locations_count = len(locations)
        
        # Keep track of last location to calculate return trip
        last_lat = current_lat
        last_lon = current_lon

        for _i in range(locations_count):
            nearest_dist = float('inf')
            nearest_idx = -1

            # Find nearest unvisited neighbor
            for i, loc in enumerate(locations):
                if not loc['visited']:
                    dist = self._haversine_distance(current_lat, current_lon, loc['lat'], loc['lon'])
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_idx = i
            
            if nearest_idx != -1:
                # Update State
                task_data = locations[nearest_idx]
                task_data['visited'] = True
                task = task_data['task']
                
                # Update Sequence & Travel Duration
                travel_hours = nearest_dist / 50.0  # Avg speed 50km/h
                arrival_time = current_time + timedelta(hours=travel_hours)
                
                # Advance Current Time (Arrival + Intervention)
                intervention_hours = task.intervention_duration or 1.0
                departure_time = arrival_time + timedelta(hours=intervention_hours)
                current_time = departure_time

                # Update Task
                task.write({
                    'visit_sequence': sequence_counter,
                    'travel_duration': travel_hours,
                    'estimated_arrival': arrival_time,
                })

                # Update current position for next iteration
                current_lat = task_data['lat']
                current_lon = task_data['lon']
                last_lat = current_lat
                last_lon = current_lon
                
                sequence_counter += 1
            else:
                break
        
        # 3. Calculate Return Trip
        return_dist = self._haversine_distance(last_lat, last_lon, start_coords[0], start_coords[1])
        return_travel_hours = return_dist / 50.0
        return_time = current_time + timedelta(hours=return_travel_hours)

        # Format return time for display (User's timezone handling is usually auto in frontend but specific format helps)
        # Using Odoo's default formatting via fields_view_get or simple str
        # Better to just pass the stringified datetime for the message
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Route Optimized'),
                'message': _('Route optimized for %d tasks.\nEstimated Return Time: %s') % (len(tasks), return_time.strftime('%Y-%m-%d %H:%M')),
                'sticky': True, # Stick so user sees the return time
                'type': 'success',
            }
        }
