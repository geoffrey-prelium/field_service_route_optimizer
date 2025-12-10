{
    'name': 'Field Service Smart Route Optimizer',
    'version': '1.2',
    'category': 'Field Service / Logistics',
    'summary': 'Optimize technician routes using Nearest Neighbor algorithm',
    'description': """
        Optimizes the route for technicians or delivery drivers by reordering tasks
        to minimize travel distance (Simplified TSP).
        
        Features:
        - Technician Start Address configuration
        - 'Optimize Route' button on Tasks
        - Automatic sequence reordering
        - Distance calculation using Haversine formula
        - Estimated Arrival Time calculation
        - Intervention Duration management
        - Wizard to specify Start Time and see Return Time
    """,
    'depends': ['project', 'base_geolocalize', 'industry_fsm'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/add_route_tasks_views.xml',
        'views/res_users_views.xml',
        'views/route_views.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
