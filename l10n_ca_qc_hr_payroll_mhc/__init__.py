# Part of MHC. See LICENSE file for full copyright and licensing details.

from . import models
from . import wizard


def _post_init_hook(env):
    """Archive default salary rules auto-added to Quebec structure."""
    qc_structure = env.ref('l10n_ca_qc_hr_payroll_mhc.hr_payroll_structure_qc_employee_salary', raise_if_not_found=False)
    if qc_structure:
        default_codes = ['BASIC', 'GROSS', 'NET', 'ATTACH_SALARY', 'ASSIG_SALARY', 'CHILD_SUPPORT', 'DEDUCTION', 'REIMBURSEMENT']
        default_rules = env['hr.salary.rule'].search([
            ('struct_id', '=', qc_structure.id),
            ('code', 'in', default_codes),
        ])
        if default_rules:
            default_rules.active = False
