# Part of MHC. See LICENSE file for full copyright and licensing details.

{
    'name': 'Canada - Payroll EFT (CPA Standard 005)',
    'version': '19.0.1.0.2',
    'category': 'Human Resources/Payroll',
    'summary': 'Generate CPA Standard 005 EFT files to pay employees via Canadian banks (RBC, TD, BMO, Scotia, CIBC, NBC, Desjardins, etc.)',
    'depends': [
        'l10n_ca_hr_payroll_except_QC',
        'hr_work_entry_enterprise',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/res_company_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payslip_run_views.xml',
        'wizard/eft_generate_wizard_views.xml',
    ],
    'author': 'MapleHorn Consulting Inc.',
    'license': 'OPL-1',
    'installable': True,
}
