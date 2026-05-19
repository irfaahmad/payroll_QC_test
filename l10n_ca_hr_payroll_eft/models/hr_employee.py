# Part of MHC. See LICENSE file for full copyright and licensing details.

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    l10n_ca_bank_institution = fields.Char(
        'Institution Number',
        size=3,
        groups='hr.group_hr_user',
        help='3-digit Canadian institution (bank) number. e.g. 001=BMO, 002=Scotiabank, 003=RBC, 004=TD, 010=CIBC, 006=NBC, 815=Desjardins.',
    )
    l10n_ca_bank_transit = fields.Char(
        'Transit (Branch) Number',
        size=5,
        groups='hr.group_hr_user',
        help='5-digit branch transit number from the void cheque.',
    )
    l10n_ca_bank_account = fields.Char(
        'Bank Account Number',
        size=12,
        groups='hr.group_hr_user',
        help='Account number from the void cheque (1–12 digits, depends on bank).',
    )
    l10n_ca_pay_method = fields.Selection(
        [
            ('eft', 'Direct Deposit (EFT)'),
            ('cheque', 'Paper Cheque'),
            ('cash', 'Cash'),
        ],
        string='Pay Method',
        default='eft',
        required=True,
        groups='hr.group_hr_user',
        help='Employees set to anything other than EFT are skipped when generating the EFT file.',
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    @api.constrains(
        'l10n_ca_bank_institution',
        'l10n_ca_bank_transit',
        'l10n_ca_bank_account',
        'l10n_ca_pay_method',
    )
    def _check_l10n_ca_bank(self):
        for emp in self:
            if emp.l10n_ca_bank_institution and not re.fullmatch(r'\d{3}', emp.l10n_ca_bank_institution):
                raise ValidationError(_('Institution number must be exactly 3 digits.'))
            if emp.l10n_ca_bank_transit and not re.fullmatch(r'\d{5}', emp.l10n_ca_bank_transit):
                raise ValidationError(_('Transit number must be exactly 5 digits.'))
            if emp.l10n_ca_bank_account and not re.fullmatch(r'\d{1,12}', emp.l10n_ca_bank_account):
                raise ValidationError(_('Account number must be 1–12 digits.'))

    # ------------------------------------------------------------------
    # Sync custom Canadian bank fields → native res.partner.bank record
    # so Odoo's payroll/accounting "Missing bank account on employee"
    # check passes and the user only enters the info once.
    # ------------------------------------------------------------------
    def _l10n_ca_sync_partner_bank(self):
        """Create / update a res.partner.bank from the Canadian bank fields.

        Stores routing as the de-facto Canadian convention:
            <transit>-<institution>-<account>
        on the employee's work_contact_id (or user partner if no work contact).
        Idempotent: if a matching record already exists, does nothing.
        """
        Bank = self.env['res.partner.bank']
        for emp in self:
            if not (emp.l10n_ca_bank_institution
                    and emp.l10n_ca_bank_transit
                    and emp.l10n_ca_bank_account):
                continue
            partner = emp.work_contact_id or (emp.user_id and emp.user_id.partner_id)
            if not partner:
                continue
            acc_number = (
                f'{emp.l10n_ca_bank_transit}-'
                f'{emp.l10n_ca_bank_institution}-'
                f'{emp.l10n_ca_bank_account}'
            )
            existing = Bank.search([
                ('partner_id', '=', partner.id),
                ('acc_number', '=', acc_number),
            ], limit=1)
            if existing:
                # Make sure it's allowed for outbound payments
                if not existing.allow_out_payment:
                    existing.sudo().write({'allow_out_payment': True})
                continue
            # Disable any older Canadian-format bank records on this partner
            # so we don't accumulate stale ones after the user edits the fields.
            old = Bank.search([
                ('partner_id', '=', partner.id),
                ('acc_number', '=like', '_____-___-%'),  # transit-inst-account shape
            ])
            if old:
                old.sudo().write({'allow_out_payment': False})
            Bank.sudo().create({
                'partner_id': partner.id,
                'acc_number': acc_number,
                'acc_holder_name': emp.name,
                'allow_out_payment': True,
            })

    @api.model_create_multi
    def create(self, vals_list):
        emps = super().create(vals_list)
        emps._l10n_ca_sync_partner_bank()
        return emps

    def write(self, vals):
        res = super().write(vals)
        if any(k in vals for k in (
            'l10n_ca_bank_institution',
            'l10n_ca_bank_transit',
            'l10n_ca_bank_account',
            'name',  # keep acc_holder_name in sync if employee renamed
        )):
            self._l10n_ca_sync_partner_bank()
        return res
