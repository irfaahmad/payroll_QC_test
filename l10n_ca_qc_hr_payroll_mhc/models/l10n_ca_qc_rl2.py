# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class L10nCaQcRl2Slip(models.Model):
    _name = 'l10n_ca_qc.rl2.slip'
    _description = 'Quebec RL-2 Slip (Relevé 2 — Retirement and Annuity Income)'
    _order = 'year desc, recipient_name'

    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True,
    )
    year = fields.Selection(
        selection=[
            ('2024', '2024'),
            ('2025', '2025'),
            ('2026', '2026'),
            ('2027', '2027'),
            ('2028', '2028'),
            ('2029', '2029'),
            ('2030', '2030'),
        ],
        string='Tax Year',
        required=True,
        default=lambda self: str(fields.Date.today().year),
    )
    recipient_name = fields.Char(string='Recipient Name', required=True)
    recipient_sin = fields.Char(string='Recipient SIN')
    recipient_address = fields.Text(string='Recipient Address')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency',
        readonly=True,
    )
    summary_id = fields.Many2one(
        comodel_name='l10n_ca_qc.rl2.summary',
        string='RL-2 Summary',
        ondelete='set null',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('sent', 'Sent'),
        ],
        string='Status',
        default='draft',
        required=True,
        readonly=True,
    )

    # RL-2 Box fields
    box_a = fields.Monetary(
        string='Box A — Pension/Superannuation',
        currency_field='currency_id',
    )
    box_b = fields.Monetary(
        string='Box B — Lump-Sum Payments',
        currency_field='currency_id',
    )
    box_c = fields.Monetary(
        string='Box C — Other Income',
        currency_field='currency_id',
    )
    box_d = fields.Monetary(
        string='Box D — Quebec Income Tax Withheld',
        currency_field='currency_id',
    )
    box_e = fields.Monetary(
        string='Box E — Annuities',
        currency_field='currency_id',
    )
    box_f = fields.Monetary(
        string='Box F — Self-Employed Commissions',
        currency_field='currency_id',
    )
    box_g = fields.Monetary(
        string='Box G — Fees for Services',
        currency_field='currency_id',
    )

    @api.depends('year', 'recipient_name')
    def _compute_name(self):
        for rec in self:
            rec.name = 'RL2 - %s - %s' % (rec.year or '', rec.recipient_name or '')

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_send(self):
        self.write({'state': 'sent'})
