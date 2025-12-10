import logging
from math import radians, cos, sin, asin, sqrt
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FieldServiceRoute(models.Model):
    _name = 'field.service.route'
    _description = 'Field Service Route'
    _order = 'start_datetime desc'

    name = fields.Char(string="Route Name", required=True, default=lambda self: fields.Date.today())
    user_id = fields.Many2one('res.users', string="Driver/Technician", default=lambda self: self.env.user, required=True)
    start_datetime = fields.Datetime(string="Start Date & Time", required=True, default=fields.Datetime.now)
    
    task_ids = fields.One2many('project.task', 'route_id', string="Tasks")
    
    total_travel_duration = fields.Float(string="Total Travel (Hours)", compute='_compute_totals', store=True)
    total_intervention_duration = fields.Float(string="Total Intervention (Hours)", compute='_compute_totals', store=True)
    return_travel_duration = fields.Float(string="Return Travel (Hours)", readonly=True)
    end_datetime = fields.Datetime(string="Estimated Return Time", compute='_compute_totals', store=True)

    @api.depends('task_ids.travel_duration', 'task_ids.intervention_duration', 'start_datetime', 'return_travel_duration')
    def _compute_totals(self):
        for route in self:
            total_travel = sum(route.task_ids.mapped('travel_duration'))
            total_intervention = sum(route.task_ids.mapped('intervention_duration'))
            
            route.total_travel_duration = total_travel + route.return_travel_duration
            route.total_intervention_duration = total_intervention
            
            if route.start_datetime:
                # End Time = Start + All Travels (including return) + All Interventions
                route.end_datetime = route.start_datetime + timedelta(hours=route.total_travel_duration + total_intervention)
            else:
                route.end_datetime = False

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

    def action_optimize_route(self):
        self.ensure_one()
        tasks = self.task_ids
        if not tasks:
            raise UserError(_("No tasks in this route."))

        user_start_partner = self.user_id.default_start_address_id
        if not user_start_partner:
            raise UserError(_("Please configure a Default Start Address for user %s.") % self.user_id.name)

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
        
        self.write({
            'return_travel_duration': return_travel_hours,
        })
        
        # Recalculate end_datetime via compute
        self._compute_totals()
        
        return_time = self.end_datetime

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Route Optimized'),
                'message': _('Optimization complete. Return Time: %s') % (return_time.strftime('%Y-%m-%d %H:%M') if return_time else 'N/A'),
                'sticky': False,
                'type': 'success',
            }
        }

    def action_open_google_maps(self):
        self.ensure_one()
        if not self.task_ids:
            raise UserError(_("No tasks to map."))
        
        user_start_partner = self.user_id.default_start_address_id
        if not user_start_partner:
            raise UserError(_("No Start Address found for user %s") % self.user_id.name)
            
        # Origin
        origin = f"{user_start_partner.partner_latitude},{user_start_partner.partner_longitude}"
        
        # Destination (Same as origin for round trip)
        destination = origin
        
        # Waypoints (Ordered by visit_sequence)
        # Google Maps limits waypoints (approx 10-20 depending on platform). 
        # We'll take the first 20 just in case to avoid URL length issues or API limits in free mode.
        sorted_tasks = self.task_ids.sorted('visit_sequence')
        waypoints_list = []
        for task in sorted_tasks:
            if task.partner_id.partner_latitude and task.partner_id.partner_longitude:
                waypoints_list.append(f"{task.partner_id.partner_latitude},{task.partner_id.partner_longitude}")
        
        waypoints = "|".join(waypoints_list[:20]) # Limit to 20 to be safe
        
        # Construct URL
        # https://www.google.com/maps/dir/?api=1&origin=...&destination=...&waypoints=...&travelmode=driving
        
        url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints}&travelmode=driving"
        
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
