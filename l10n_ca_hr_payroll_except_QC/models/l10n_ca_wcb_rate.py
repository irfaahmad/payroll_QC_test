# Part of MHC. See LICENSE file for full copyright and licensing details.

from __future__ import annotations

from datetime import date as date_type

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# Full list of Canadian provinces and territories (including QC for CNESST)
PROVINCE_SELECTION = [
    ('AB', 'Alberta'),
    ('BC', 'British Columbia'),
    ('MB', 'Manitoba'),
    ('NB', 'New Brunswick'),
    ('NL', 'Newfoundland and Labrador'),
    ('NS', 'Nova Scotia'),
    ('NT', 'Northwest Territories'),
    ('NU', 'Nunavut'),
    ('ON', 'Ontario'),
    ('PE', 'Prince Edward Island'),
    ('QC', 'Quebec (CNESST)'),
    ('SK', 'Saskatchewan'),
    ('YT', 'Yukon'),
]


class L10nCaWcbRate(models.Model):
    """Manual-entry WCB / CNESST employer rate record.

    One record per (company, province, effective date). Create a new dated
    record whenever the employer's assessment rate changes — never edit a
    historical record.  The salary rule reads the record whose date_from is
    closest to (and not after) the payslip end date.
    """

    _name = 'l10n.ca.wcb.rate'
    _description = 'Canadian WCB / CNESST Employer Rate'
    _order = 'company_id, province, date_from desc'

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade',
    )
    province = fields.Selection(
        selection=PROVINCE_SELECTION,
        string='Province / Territory',
        required=True,
    )
    board_name = fields.Char(
        string='Board Name',
        help='Name of the workers compensation board (e.g. WSIB, WorkSafeBC, CNESST).',
    )
    classification_unit = fields.Char(
        string='Classification / Rate Group',
        help="Employer's WCB classification unit or industry rate group from the assessment letter.",
    )
    employer_rate = fields.Float(
        string='Employer Rate (%)',
        digits=(6, 4),
        required=True,
        help='Employer WCB / CNESST rate as a percentage (e.g. enter 1.95 for 1.95%).',
    )
    max_assessable_earnings = fields.Monetary(
        string='Maximum Assessable Earnings',
        currency_field='currency_id',
        required=True,
        help='Annual ceiling on insurable / assessable earnings for this province.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    date_from = fields.Date(
        string='Effective From',
        required=True,
        default=fields.Date.today,
    )
    date_to = fields.Date(
        string='Effective To',
        help='Leave blank if this rate is currently in effect.',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    notes = fields.Text(
        string='Notes',
        help='Internal notes (e.g. reference to the assessment letter).',
    )

    # ------------------------------------------------------------------
    # Computed fields
    # ------------------------------------------------------------------

    @api.depends('province', 'board_name', 'employer_rate', 'date_from')
    def _compute_name(self):
        province_labels = dict(PROVINCE_SELECTION)
        for rec in self:
            prov = province_labels.get(rec.province, rec.province or '')
            board = rec.board_name or ''
            rate = rec.employer_rate or 0.0
            date = rec.date_from or fields.Date.today()
            if board:
                rec.name = f'{prov} {board} {rate:.4f}% (from {date})'
            else:
                rec.name = f'{prov} {rate:.4f}% (from {date})'

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_to and rec.date_from and rec.date_to < rec.date_from:
                raise ValidationError(
                    _("'Effective To' (%s) must be on or after 'Effective From' (%s).")
                    % (rec.date_to, rec.date_from)
                )

    @api.constrains('employer_rate', 'max_assessable_earnings')
    def _check_positive(self):
        for rec in self:
            if rec.employer_rate < 0:
                raise ValidationError(
                    _('Employer rate must be zero or positive (got %.4f%%).')
                    % rec.employer_rate
                )
            if rec.max_assessable_earnings <= 0:
                raise ValidationError(
                    _('Maximum assessable earnings must be greater than zero (got %s).')
                    % rec.max_assessable_earnings
                )

    # ------------------------------------------------------------------
    # Helper API
    # ------------------------------------------------------------------

    @api.model
    def get_current_rate(self, company, province, date=None):
        """Return the WCB rate record in effect for (company, province) on date.

        Returns an empty recordset if no matching active record is found.

        :param company: res.company record
        :param province: two-letter province code (e.g. 'ON', 'QC')
        :param date: effective date (date object or None; defaults to today)
        """
        if date is None:
            date = date_type.today()
        return self.search(
            [
                ('company_id', '=', company.id),
                ('province', '=', province),
                ('date_from', '<=', date),
                '|',
                ('date_to', '=', False),
                ('date_to', '>=', date),
                ('active', '=', True),
            ],
            order='date_from desc',
            limit=1,
        )
