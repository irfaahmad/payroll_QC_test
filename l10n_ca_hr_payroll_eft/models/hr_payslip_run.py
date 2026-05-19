# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    # --- EFT tracking fields ---
    l10n_ca_eft_generated = fields.Boolean(
        'EFT File Generated', readonly=True, copy=False)
    l10n_ca_eft_file_number = fields.Integer(
        'File Creation #', readonly=True, copy=False)
    l10n_ca_eft_settlement_date = fields.Date(
        'Settlement (Pay) Date', copy=False)
    l10n_ca_eft_payment_id = fields.Many2one(
        'account.payment', string='EFT Bulk Payment', readonly=True, copy=False)
    l10n_ca_eft_attachment_id = fields.Many2one(
        'ir.attachment', string='EFT File (raw)', readonly=True, copy=False)

    # --- Convenience fields surfaced on the form for re-download ---
    l10n_ca_eft_file = fields.Binary(
        string='EFT File',
        related='l10n_ca_eft_attachment_id.datas',
        readonly=True,
        attachment=False,
    )
    l10n_ca_eft_filename = fields.Char(
        string='EFT Filename',
        related='l10n_ca_eft_attachment_id.name',
        readonly=True,
    )

    def action_generate_eft(self):
        """Open the EFT generation wizard pre-filled with this pay run."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate EFT File'),
            'res_model': 'l10n.ca.eft.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payslip_run_id': self.id,
                'default_settlement_date': self.l10n_ca_eft_settlement_date or fields.Date.today(),
            },
        }

    def action_download_eft(self):
        """Re-download the previously generated EFT file."""
        self.ensure_one()
        if not self.l10n_ca_eft_attachment_id:
            raise UserError(_('No EFT file has been generated for this pay run yet.'))
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.l10n_ca_eft_attachment_id.id}?download=true',
            'target': 'self',
        }
