# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class L10nCaQcGarnishment(models.Model):
    _name = 'l10n_ca_qc.garnishment'
    _description = 'Quebec Garnishment / Court-Ordered Deduction'
    _order = 'priority, employee_id'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        required=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    garnishment_type = fields.Selection(
        selection=[
            ('child_support', 'Child Support'),
            ('alimony', 'Alimony / Spousal Support'),
            ('tax_debt', 'Tax Debt'),
            ('other', 'Other Court Order'),
        ],
        string="Garnishment Type",
        required=True,
        default='child_support',
    )
    description = fields.Char(
        string="Description / Reference",
        help="Court order number or description for this garnishment.",
    )
    amount = fields.Float(
        string="Fixed Amount",
        digits=(16, 2),
        help="Fixed dollar amount to deduct per pay period (used when is_percentage is False).",
    )
    is_percentage = fields.Boolean(
        string="Percentage Based",
        default=False,
        help="If checked, deduct a percentage of disposable net pay instead of a fixed amount.",
    )
    percentage = fields.Float(
        string="Percentage (%)",
        digits=(6, 4),
        help="Percentage of disposable net pay to deduct (e.g. 0.25 for 25%).",
    )
    priority = fields.Integer(
        string="Priority",
        default=10,
        help="Lower number = higher priority. Child support typically takes priority.",
    )
    start_date = fields.Date(
        string="Start Date",
        required=True,
    )
    end_date = fields.Date(
        string="End Date",
        help="Leave blank for indefinite garnishment.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    balance_remaining = fields.Float(
        string="Remaining Balance",
        digits=(16, 2),
        help="Total remaining balance to be collected (0 = ongoing/indefinite).",
    )
    exempt_amount = fields.Float(
        string="Exempt Amount (per period)",
        digits=(16, 2),
        help="Minimum take-home pay per pay period protected under Quebec Civil Code.",
    )
    total_deducted = fields.Float(
        string="Total Deducted to Date",
        digits=(16, 2),
        readonly=True,
        help="Running total of all amounts deducted under this garnishment order.",
    )
