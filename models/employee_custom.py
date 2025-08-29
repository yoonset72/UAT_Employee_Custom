from odoo import models, fields, api, _
import logging, re

_logger = logging.getLogger(__name__)

class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_number = fields.Char(string="Employee ID Number")
    nrc_state_code = fields.Selection([
        ('၁', '၁'), ('၂', '၂'),
        ('၃', '၃'), ('၄', '၄'),
        ('၅', '၅'), ('၆', '၆'),
        ('၇', '၇'), ('၈', '၈'),
        ('၉', '၉'), ('၁၀', '၁၀'),
        ('၁၁', '၁၁'), ('၁၂', '၁၂'),
        ('၁၃', '၁၃'), ('၁၄', '၁၄'),
    ], string="NRC State Code")

    nrc_township_id = fields.Many2one(
        'nrc.township',
        string="Township Code",
        domain="[('state_code', '=', nrc_state_code)]"
    )

    nrc_citizenship = fields.Selection([
        ('နိုင်', 'နိုင်'),
        ('ဧည့်', 'ဧည့်'),
        ('ပြု', 'ပြု'),
    ], string="Citizenship")

    nrc_number = fields.Char(string="NRC Number (6 digits)")

    nrc_full = fields.Char(string="Full NRC", compute="_compute_nrc_full", store=True)

    @api.depends('nrc_state_code', 'nrc_township_id.code', 'nrc_citizenship', 'nrc_number')
    def _compute_nrc_full(self):
        for rec in self:
            if all([
                rec.nrc_state_code,
                rec.nrc_township_id and rec.nrc_township_id.code,
                rec.nrc_citizenship,
                rec.nrc_number
            ]):
                rec.nrc_full = f"{rec.nrc_state_code}/{rec.nrc_township_id.code}({rec.nrc_citizenship}){rec.nrc_number}"
            else:
                rec.nrc_full = ""

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._parse_nrc_full(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._parse_nrc_full(vals)
        return super().write(vals)

    def _parse_nrc_full(self, vals):
        nrc_full = vals.get('nrc_full')
        if not nrc_full or not isinstance(nrc_full, str):
            return

        match = re.match(r'(\d+)/([^\(]+)\((နိုင်|ဧည့်|ပြု)\)(\d+)', nrc_full)
        if not match:
            _logger.warning("Invalid NRC format: %s", nrc_full)
            return

        state_code = match.group(1).strip()
        township_code = match.group(2).strip()
        citizenship = match.group(3).strip()
        nrc_number = match.group(4).strip()

        vals['nrc_state_code'] = state_code
        vals['nrc_citizenship'] = citizenship
        vals['nrc_number'] = nrc_number

        township = self.env['nrc.township'].search([('code', '=', township_code)], limit=1)
        if township:
            vals['nrc_township_id'] = township.id
        else:
            _logger.warning("Township not found for code: %s", township_code)

    join_date = fields.Date(string="Join Date")
    off_day = fields.Many2many('day.selection', string='Off Day')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Employee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            for field in res['fields']:
                if field == 'leave_manager_id':
                    res['fields'][field]['string'] = 'Approver'
        return res
    
    @api.onchange('department_id')
    def _onchange_department_set_leave_manager(self):
        for rec in self:
            manager = rec.department_id.manager_id
            if manager:
                if not manager.user_id:
                    # Try to create a user for the manager if none exists
                    try:
                        login_email = manager.work_email or (manager.name.lower().replace(" ", "") + '@agbcommunication.com')
                        user = self.env['res.users'].create({
                            'name': manager.name,
                            'login': login_email,
                            'email': manager.work_email or False,
                            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
                            'employee_id': manager.id,
                        })
                        manager.user_id = user
                        rec.leave_manager_id = user
                        _logger.info(f"Created user {user.login} for department manager {manager.name}")
                    except Exception as e:
                        _logger.error(f"Failed to create user for manager {manager.name}: {e}")
                        rec.leave_manager_id = False
                else:
                    rec.leave_manager_id = manager.user_id
                    _logger.info(f"Set existing user {manager.user_id.name} as leave manager for {rec.name}")
            else:
                rec.leave_manager_id = False
                _logger.info(f"No manager found for department {rec.department_id.name if rec.department_id else 'N/A'}")

   

    hr_officer_names = fields.Char(
        string="Time Off Officers",
        compute='_compute_hr_officer_names',
        store=True
    )

    @api.depends('department_id')
    def _compute_hr_officer_names(self):
        for rec in self:
            names = []
            hr_dept = self.env['hr.department'].search([('name', '=', 'Human Resources')], limit=1)
            if hr_dept:
                # Add HR employees
                hr_employees = hr_dept.member_ids
                names = hr_employees.mapped('name')
                # Add HR manager if not already included
                if hr_dept.manager_id and hr_dept.manager_id.name not in names:
                    names.append(hr_dept.manager_id.name)
            rec.hr_officer_names = ', '.join(names) if names else ''

    personal_email = fields.Char(string="Email")
    personal_phone = fields.Char(string='Phone')
    home_address = fields.Char(string=_('Home Address'))
    bank_account = fields.Char(string=_('Bank Account'))
    certification_ids = fields.Many2many(
        'certification',
        string="Certifications"
    )


    resource_calendar_ids = fields.Many2many(
        'resource.calendar',
        'employee_calendar_rel',  # relation table name
        'employee_id',            # column for employee
        'calendar_id',            # column for calendar
        string='Working Hours'
    )

    