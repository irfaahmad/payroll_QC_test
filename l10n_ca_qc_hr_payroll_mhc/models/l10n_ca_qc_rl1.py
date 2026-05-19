# Part of MHC. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class L10nCaQcRl1Slip(models.Model):
    _name = 'l10n_ca_qc.rl1.slip'
    _description = 'Quebec RL-1 Slip (Relevé 1)'
    _order = 'name desc'

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self._default_name(),
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company,
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
        string="Tax Year",
        required=True,
        default=lambda self: str(fields.Date.today().year),
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('generated', 'Generated'),
            ('submitted', 'Submitted'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        default='draft',
        required=True,
        readonly=True,
    )
    # RL-1 Boxes
    box_a = fields.Float(string="Box A — Employment Income", digits=(16, 2))
    box_b = fields.Float(string="Box B — QPP Contributions", digits=(16, 2))
    box_c = fields.Float(string="Box C — EI Premiums", digits=(16, 2))
    box_d = fields.Float(string="Box D — RPP Contributions", digits=(16, 2), default=0.0)
    box_e = fields.Float(string="Box E — Quebec Income Tax Withheld", digits=(16, 2))
    box_g = fields.Float(string="Box G — Union Dues", digits=(16, 2))
    box_h = fields.Float(string="Box H — QPIP Premiums", digits=(16, 2))
    box_i = fields.Float(string="Box I — Commissions", digits=(16, 2))
    box_j = fields.Float(string="Box J — Net Federal Supplements", digits=(16, 2), default=0.0)
    box_l = fields.Float(string="Box L — Other Taxable Benefits", digits=(16, 2), default=0.0)
    box_o_code = fields.Char(string="Box O — Code")
    box_o_amount = fields.Float(string="Box O — Amount", digits=(16, 2))
    summary_id = fields.Many2one(
        comodel_name='l10n_ca_qc.rl1.summary',
        string="RL-1 Summary",
        ondelete='set null',
    )

    @api.model
    def _default_name(self):
        year = fields.Date.today().year
        seq = self.env['ir.sequence'].next_by_code('l10n_ca_qc.rl1.slip') or '001'
        return 'RL1-%s-%s' % (year, seq)

    def action_generate(self):
        for slip in self:
            date_from = fields.Date.from_string('%s-01-01' % slip.year)
            date_to = fields.Date.from_string('%s-12-31' % slip.year)
            payslips = self.env['hr.payslip'].search([
                ('employee_id', '=', slip.employee_id.id),
                ('date_from', '>=', date_from),
                ('date_to', '<=', date_to),
                ('state', 'in', ['done', 'paid']),
            ])
            lines = payslips.mapped('line_ids')

            def _sum_lines(codes):
                total = sum(
                    l.total for l in lines if l.code in codes
                )
                return total

            slip.box_a = _sum_lines(['GROSS_QC'])
            slip.box_b = abs(sum(
                l.total for l in lines if l.code in ('QPP_EE', 'QPP2_EE')
            ))
            slip.box_c = abs(sum(
                l.total for l in lines if l.code == 'EI_EE_QC'
            ))
            slip.box_d = abs(sum(
                l.total for l in lines if l.code == 'RPP_QC'
            ))
            slip.box_e = abs(sum(
                l.total for l in lines if l.code == 'PROV_TAX_QC'
            ))
            slip.box_g = abs(sum(
                l.total for l in lines if l.code == 'UNION_QC'
            ))
            slip.box_h = abs(sum(
                l.total for l in lines if l.code == 'QPIP_EE'
            ))
            # Commissions from payslip input amounts
            commission_inputs = payslips.mapped('input_line_ids').filtered(
                lambda i: i.code == 'COMMISSION_QC'
            )
            slip.box_i = sum(i.amount for i in commission_inputs)
            # Box L — Other taxable benefits
            slip.box_l = abs(sum(
                l.total for l in lines if l.code == 'TAXABLE_BENEFITS_QC'
            ))
            slip.state = 'generated'

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
