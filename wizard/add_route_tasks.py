from odoo import models, fields, api

class AddRouteTasks(models.TransientModel):
    _name = 'field.service.route.add.tasks'
    _description = 'Add Tasks to Route'

    task_ids = fields.Many2many('project.task', string="Tasks", domain="[('route_id', '=', False)]")

    def action_add_tasks(self):
        """Action to add selected tasks to the active route."""
        self.ensure_one()
        active_route_id = self.env.context.get('active_id')
        if active_route_id:
            route = self.env['field.service.route'].browse(active_route_id)
            if self.task_ids:
                self.task_ids.write({'route_id': route.id})
        return {'type': 'ir.actions.act_window_close'}
