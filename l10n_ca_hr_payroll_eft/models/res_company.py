# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ca_eft_bank_format = fields.Selection(
        [
            ('rbc', 'RBC Royal Bank (ACH 1464)'),
            ('td', 'TD Canada Trust (ACS 1464)'),
            ('bmo', 'BMO Bank of Montreal (Direct 1464)'),
            ('scotia', 'Scotiabank (ScotiaConnect 1464)'),
            ('cibc', 'CIBC (1464)'),
            ('nbc', 'National Bank of Canada (1464)'),
            ('desjardins', 'Desjardins (AFT 1464)'),
            ('generic', 'Generic CPA 005 (1464)'),
        ],
        string='Bank EFT Format',
        default='rbc',
        required=True,
        help='Choose the format dialect that matches your bank. All are CPA Standard 005 1464-byte format with bank-specific filler/sundry differences.',
    )
    l10n_ca_eft_originator_id = fields.Char(
        'CPA Originator ID',
        size=10,
        help='10-character originator ID assigned by your bank when you sign the EFT agreement.',
    )
    l10n_ca_eft_short_name = fields.Char('Originator Short Name', size=15)
    l10n_ca_eft_long_name = fields.Char('Originator Long Name', size=30)
    l10n_ca_eft_originator_inst = fields.Char(
        'Originator Institution',
        size=3,
        help="3-digit institution number of the company's payroll bank account.",
    )
    l10n_ca_eft_originator_transit = fields.Char('Originator Transit', size=5)
    l10n_ca_eft_originator_account = fields.Char('Originator Account Number', size=12)
    l10n_ca_eft_data_centre = fields.Selection(
        [
            ('00450', 'Halifax'),
            ('00490', 'Montreal'),
            ('00540', 'Toronto'),
            ('00550', 'Regina'),
            ('00580', 'Winnipeg'),
            ('00590', 'Calgary'),
            ('00650', 'Vancouver'),
        ],
        string='Destination Data Centre',
        help='Bank data-centre routing code (your bank tells you which to use).',
    )
    l10n_ca_eft_currency = fields.Selection([('CAD', 'CAD'), ('USD', 'USD')], default='CAD', string='EFT Currency')
    l10n_ca_eft_file_counter = fields.Integer(
        'Next File Creation Number',
        default=1,
        help='Auto-incremented for each EFT file generated. Some banks require this be strictly sequential.',
    )
    l10n_ca_eft_bank_journal_id = fields.Many2one(
        'account.journal',
        string='EFT Bank Journal',
        domain="[('type', '=', 'bank'), ('company_id', '=', id)]",
        help='Bank journal that funds the EFT debit. Used to post the bulk payroll account.payment.',
    )
    l10n_ca_eft_clearing_account_id = fields.Many2one(
        'account.account',
        string='Net Pay Clearing Account',
        help="Defaults to account 2380 (Net Pay Clearing) created by the base payroll module. The EFT payment debits this account and credits the bank journal's outstanding-payments account.",
    )
