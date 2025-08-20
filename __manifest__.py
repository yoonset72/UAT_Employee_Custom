{
    'name': 'Employee Custom',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'summary': 'Customization of Employee module on odoo15',
    'description': 'Adds and hides customized fields to employee profile.',
    'category': 'Human Resources',
    'author': 'AGB Communication',
    'depends': ['website', 'base', 'hr', 'hr_holidays'],
    'data': [
        'views/employee_view.xml',
        'security/ir.model.access.csv',
        'data/nrc_township_data.xml',
        'security/off_day_selection_security.xml',
    ],
    'installable': True,
    'application': False,
}
