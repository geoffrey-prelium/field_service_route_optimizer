from odoo import models, fields, api

class AddRouteTasks(models.TransientModel):
    _name = 'field.service.route.add.tasks'
    _description = 'Add Tasks to Route'

    task_ids = fields.Many2many('project.task', string="Tasks", domain="[('route_id', '=', False)]")

    @api.model
    def default_get(self, fields_list):
        """Automatically suggest tasks that are not yet on any route."""
        res = super().default_get(fields_list)
        if 'task_ids' in fields_list:
            unassigned_tasks = self.env['project.task'].search([('route_id', '=', False)])
            if unassigned_tasks:
                res['task_ids'] = [(6, 0, unassigned_tasks.ids)]
        return res

    def action_add_tasks(self):
        """Action to add selected tasks to the active route."""
        self.ensure_one()
        active_route_id = self.env.context.get('active_id')
        if active_route_id:
            route = self.env['field.service.route'].browse(active_route_id)
            if self.task_ids:
                self.task_ids.write({'route_id': route.id})
        return {'type': 'ir.actions.act_window_close'}
