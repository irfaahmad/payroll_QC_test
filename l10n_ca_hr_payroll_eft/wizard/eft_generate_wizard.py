# Part of MHC. See LICENSE file for full copyright and licensing details.

import base64

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..models.cpa005 import get_builder


class EftGenerateWizard(models.TransientModel):
    _name = 'l10n.ca.eft.wizard'
    _description = 'Generate CPA 005 EFT File'

    payslip_run_id = fields.Many2one(
        'hr.payslip.run',
        string='Pay Run',
        required=True,
        # Accept every "ready or beyond" state across Odoo 17/18/19 minor
        # versions. Variants seen in the wild: 'close', 'done', 'paid',
        # '01_ready', '02_done', '02_close', '03_paid'. Excluding only the
        # "still being prepared" / cancelled states is the most robust filter.
        domain="[('state', 'not in', ('new', 'draft', 'verify', 'cancel', 'cancelled'))]",
    )
    settlement_date = fields.Date(required=True, default=fields.Date.context_today)
    mark_paid = fields.Boolean(
        default=True,
        help='Set the EFT-paid payslips to state Paid after the file is generated.',
    )
    create_payment = fields.Boolean(
        default=True,
        help='Create a single account.payment for the bulk EFT debit.',
    )

    # ------------------------------------------------------------------
    # Main action
    # ------------------------------------------------------------------
    def action_generate(self):
        self.ensure_one()
        run = self.payslip_run_id
        company = run.company_id
        self._validate_company(company)

        # The batch-level domain on payslip_run_id already guarantees the
        # run is past draft/verify/cancel, which means its slips are
        # computed. Don't double-filter on slip.state — the variants drift
        # between Odoo minor versions ('done', 'validated', '02_done',
        # '02_close', '03_paid', etc.) and cause spurious eligibility
        # errors. Just exclude explicitly-cancelled slips.
        eligible = run.slip_ids.filtered(
            lambda s: s.state not in ('cancel', 'cancelled')
            and s.net_wage > 0
            and s.employee_id.l10n_ca_pay_method == 'eft'
        )
        if not eligible:
            raise UserError(_(
                'No EFT-eligible payslips in this batch '
                '(employee Pay Method must be "Direct Deposit (EFT)" and net pay > 0).'
            ))
        for slip in eligible:
            self._validate_employee(slip.employee_id)

        # ---------- build the CPA 005 file ----------
        file_number = company.l10n_ca_eft_file_counter
        BuilderCls = get_builder(company.l10n_ca_eft_bank_format)
        builder = BuilderCls(
            company,
            file_number,
            creation_date=fields.Date.context_today(self),
            settlement_date=self.settlement_date,
            currency=company.l10n_ca_eft_currency or 'CAD',
        )
        for slip in eligible:
            builder.add_credit(slip.employee_id, slip.net_wage, slip.name or str(slip.id))

        content = builder.build()
        filename = (
            f"EFT_{company.l10n_ca_eft_bank_format.upper()}_"
            f"{(run.name or str(run.id)).replace('/', '-')}_{file_number:04d}.txt"
        )

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'res_model': 'hr.payslip.run',
            'res_id': run.id,
            'datas': base64.b64encode(content),
            'mimetype': 'text/plain',
        })

        # ---------- bulk account.payment ----------
        payment = False
        if self.create_payment:
            payment = self._create_bulk_payment(company, run, eligible, file_number)

        # ---------- bump counter + flag the batch ----------
        company.sudo().l10n_ca_eft_file_counter = file_number + 1
        run.write({
            'l10n_ca_eft_generated': True,
            'l10n_ca_eft_file_number': file_number,
            'l10n_ca_eft_settlement_date': self.settlement_date,
            'l10n_ca_eft_attachment_id': attachment.id,
            'l10n_ca_eft_payment_id': payment.id if payment else False,
        })

        # ---------- mark payslips as paid ----------
        if self.mark_paid:
            # Use action_payslip_paid() if it exists (cleaner state transition);
            # fall back to a direct write otherwise.
            for slip in eligible:
                if hasattr(slip, 'action_payslip_paid'):
                    try:
                        slip.action_payslip_paid()
                        continue
                    except Exception:
                        pass
                slip.write({'state': 'paid'})

        # ---------- download the file ----------
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_company(self, company):
        required = [
            ('l10n_ca_eft_originator_id', 'CPA Originator ID'),
            ('l10n_ca_eft_short_name', 'Originator Short Name'),
            ('l10n_ca_eft_long_name', 'Originator Long Name'),
            ('l10n_ca_eft_originator_inst', 'Originator Institution'),
            ('l10n_ca_eft_originator_transit', 'Originator Transit'),
            ('l10n_ca_eft_originator_account', 'Originator Account'),
            ('l10n_ca_eft_data_centre', 'Destination Data Centre'),
            ('l10n_ca_eft_bank_journal_id', 'EFT Bank Journal'),
        ]
        missing = [label for field_name, label in required if not company[field_name]]
        if missing:
            raise UserError(
                _('Configure the EFT originator profile on the company. Missing: %s')
                % ', '.join(missing)
            )

    def _validate_employee(self, emp):
        if not (emp.l10n_ca_bank_institution and emp.l10n_ca_bank_transit and emp.l10n_ca_bank_account):
            raise UserError(
                _('Employee %s is missing Canadian bank info (Institution / Transit / Account).')
                % emp.name
            )

    # ------------------------------------------------------------------
    # Bulk payment
    # ------------------------------------------------------------------
    def _create_bulk_payment(self, company, run, slips, file_number):
        total = sum(slip.net_wage for slip in slips)

        # Resolve the clearing account (default: 2380 Net Pay Clearing)
        clearing = company.l10n_ca_eft_clearing_account_id
        if not clearing:
            # In v19 account.account is shared via company_ids (m2m), not company_id.
            # Try the new field first, fall back to the legacy single-company field.
            Account = self.env['account.account']
            clearing = Account.search(
                [('code', '=', '2380'), ('company_ids', 'in', company.id)],
                limit=1,
            )
            if not clearing:
                clearing = Account.search(
                    [('code', '=', '2380'), ('company_id', '=', company.id)],
                    limit=1,
                )
        if not clearing:
            raise UserError(_(
                'No clearing account configured for EFT and account 2380 '
                '(Net Pay Clearing) was not found. Set the EFT Clearing Account '
                'on the company form.'
            ))

        # Resolve the partner the payment is "to". For a bulk payroll debit
        # there isn't really a vendor — use the company partner so the move
        # balances cleanly. Downstream users can change it if they prefer
        # to track a "Payroll Bank" partner.
        partner = company.partner_id

        payment_vals = {
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': partner.id,
            'amount': total,
            'currency_id': company.currency_id.id,
            'date': self.settlement_date,
            'journal_id': company.l10n_ca_eft_bank_journal_id.id,
            'memo': f'Payroll EFT {run.name or run.id} (file #{file_number})',
            'destination_account_id': clearing.id,
        }

        payment = self.env['account.payment'].create(payment_vals)
        try:
            payment.action_post()
        except Exception as e:
            # Don't kill the whole wizard if posting fails (e.g. journal not
            # configured for outbound payments). Leave the payment in draft
            # and surface a clear message in the chatter on the batch.
            run.message_post(body=_(
                'EFT bulk payment created in <b>draft</b> state '
                '(could not auto-post: %s). Please review and post manually.'
            ) % e)
        return payment
