# from odoo import models, fields, api

# class Employee(models.Model):
#     _inherit = 'hr.employee'

#     time_off_approver_ids = fields.Many2many(
#         'hr.employee',
#         'hr_employee_timeoff_approver_rel',
#         'employee_id',
#         'approver_id',
#         string="Time Off Approvers"
#     )

#     @api.onchange('department_id')
#     def _onchange_department_id_set_approvers(self):
#         hr_department = self.env['hr.department'].search([('name', '=', 'Human Resources')], limit=1)
#         approvers = []

#         if hr_department:
#             # Add all employees in HR
#             hr_employees = self.env['hr.employee'].search([('department_id', '=', hr_department.id)])
#             approvers.extend(hr_employees.ids)

#             # Add HR manager explicitly if not already in list
#             if hr_department.manager_id and hr_department.manager_id.id not in approvers:
#                 approvers.append(hr_department.manager_id.id)

#         # Add the manager of the selected department
#         if self.department_id and self.department_id.manager_id:
#             manager_id = self.department_id.manager_id.id
#             if manager_id not in approvers:
#                 approvers.append(manager_id)

#         # Set approvers
#         if approvers:
#             self.time_off_approver_ids = [(6, 0, approvers)]

from odoo import models, fields, api

class Employee(models.Model):
    _inherit = 'hr.employee'

    # ➊ Where we will store the list we build
    hr_department_employees_ids = fields.Many2many(
        'hr.employee',
        string='HR Department Employees',
        readonly=True,            # make it readonly if users shouldn’t edit it
        store=True,               # keep it in DB so it’s there right after create()
        compute='_compute_hr_employees',
        depends=['leave_manager_id']    # auto‑refresh if someone later changes approver
    )

    # ➋ Compute method (runs on create, and anytime leave_manager_id changes later)
    def _compute_hr_employees(self):
        # Cache the HR department record once
        hr_dept = self.env['hr.department'].search([('name', 'ilike', 'HR')], limit=1)
        hr_emp_ids = self.env['hr.employee'].search([
            ('department_id', '=', hr_dept.id)
        ]).ids if hr_dept else []

        for rec in self:
            rec.hr_department_employees_ids = [(6, 0, hr_emp_ids)]

    # ➌ NEW: Kick off the same logic immediately after a record is created
    @api.model
    def create(self, vals):
        record = super().create(vals)
        # _compute_hr_employees is triggered automatically by Odoo
        # *but* it runs in-memory.  We call write() so the list is saved right now.
        record._compute_hr_employees()
        record.write({
            'hr_department_employees_ids': [
                (6, 0, record.hr_department_employees_ids.ids)
            ]
        })
        return record


