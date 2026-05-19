# Part of MHC. See LICENSE file for full copyright and licensing details.

{
    'name': 'Canada - Quebec Payroll',
    'countries': ['ca'],
    'category': 'Human Resources/Payroll',
    'depends': [
        'hr_payroll',
        'hr_work_entry_holidays',
        'hr_payroll_holidays',
    ],
    'version': '19.0.1.2',
    'description': """
Quebec Payroll Rules (Revenu Quebec)
=====================================

    * QPP/QPP2 (Quebec Pension Plan) - replaces CPP
    * QPIP (Quebec Parental Insurance Plan)
    * EI at Quebec reduced rate
    * Federal Income Tax (with 16.5%% Quebec abatement)
    * Quebec Provincial Income Tax (4 brackets)
    * RRSP and Union Dues pre-tax deductions
    * RPP (Registered Pension Plan) pre-tax deduction
    * Employer contributions (QPP, QPP2, QPIP, EI, CNESST, HSF, CNT)
    * Vacation Pay Accrual & Payout
    * Statutory Holiday Pay
    * Taxable Benefits (vehicle, group insurance, housing, other)
    * Garnishment / Court-Ordered Deductions
    * Retroactive Pay, Termination Pay, Severance Pay
    * Multiple Pay Frequencies (weekly, bi-weekly, semi-monthly, monthly)
    * YTD accumulation & annual maximum enforcement for QPP/QPIP/EI
    * Annual Tax Reporting: RL-1 Slips, RL-2, ROE, T4 Slips
    * Remittance Reports (TPZ-1015.R.14 style)
    * ROE XML Export (Service Canada ROE Web format)
    * T4 XML Export (CRA T619 format)
    * Bilingual Pay Stubs (EN/FR — Bill 96 compliance)
    * TP-1015.3 Quebec Provincial Claim Code
    * 2026 Revenu Quebec and CRA rates included
    """,
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_payroll_structure_type_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/hr_rule_parameters_data.xml',
        'data/hr_payslip_input_type_data.xml',
        'data/hr_salary_rule_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_version_views.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslip_templates_fr.xml',
        'views/l10n_ca_qc_rl1_views.xml',
        'views/l10n_ca_qc_rl1_summary_views.xml',
        'views/l10n_ca_qc_rl1_wizard_views.xml',
        'views/l10n_ca_qc_rl2_views.xml',
        'views/l10n_ca_qc_roe_views.xml',
        'views/l10n_ca_qc_payroll_config_views.xml',
        'views/report_rl1_templates.xml',
        'views/report_roe_templates.xml',
        'views/l10n_ca_qc_annual_reporting_menus.xml',
    ],
    'author': 'MapleHorn Consulting Inc.',
    'website': 'https://www.maplehornconsulting.com',
    'support': 'info@maplehornconsulting.com',
    'license': 'OPL-1',
    'price': 250,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'post_init_hook': '_post_init_hook',
}
