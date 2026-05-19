# Part of MHC. See LICENSE file for full copyright and licensing details.

import base64
import xml.etree.ElementTree as ET

from odoo import api, fields, models


class L10nCaQcT4Slip(models.Model):
    _name = 'l10n_ca_qc.t4.slip'
    _description = 'T4 Statement of Remuneration Paid'
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
        tracking=True,
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
            ('submitted', 'Submitted to CRA'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        default='draft',
        required=True,
        readonly=True,
    )
    # Standard T4 Boxes
    box_14 = fields.Float(string="Box 14 — Employment Income", digits=(16, 2))
    box_16 = fields.Float(string="Box 16 — Employee's QPP Contributions", digits=(16, 2), default=0.0)
    box_17 = fields.Float(string="Box 17 — Employee's QPP2 Contributions", digits=(16, 2), default=0.0)
    box_18 = fields.Float(string="Box 18 — Employee's EI Premiums", digits=(16, 2))
    box_20 = fields.Float(string="Box 20 — RPP Contributions", digits=(16, 2), default=0.0)
    box_22 = fields.Float(string="Box 22 — Income Tax Deducted (Federal)", digits=(16, 2))
    box_24 = fields.Float(string="Box 24 — EI Insurable Earnings", digits=(16, 2))
    box_26 = fields.Float(string="Box 26 — CPP/QPP Pensionable Earnings", digits=(16, 2))
    box_44 = fields.Float(string="Box 44 — Union Dues", digits=(16, 2), default=0.0)
    box_46 = fields.Float(string="Box 46 — Charitable Donations", digits=(16, 2), default=0.0)
    box_52 = fields.Float(string="Box 52 — Pension Adjustment", digits=(16, 2), default=0.0)
    box_55 = fields.Float(string="Box 55 — PPIP/QPIP Employee Premiums", digits=(16, 2))
    box_56 = fields.Float(string="Box 56 — PPIP/QPIP Insurable Earnings", digits=(16, 2))

    summary_id = fields.Many2one(
        comodel_name='l10n_ca_qc.t4.summary',
        string="T4 Summary",
        ondelete='set null',
    )

    @api.model
    def _default_name(self):
        year = fields.Date.today().year
        seq = self.env['ir.sequence'].next_by_code('l10n_ca_qc.t4.slip') or '001'
        return 'T4-%s-%s' % (year, seq)

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

            def _sum(codes):
                return abs(sum(l.total for l in lines if l.code in codes))

            def _get_param(code):
                try:
                    return self.env['hr.rule.parameter']._get_parameter_from_code(code, date_to)
                except (KeyError, ValueError):
                    return None

            gross_total = sum(l.total for l in lines if l.code == 'GROSS_QC')

            ei_max_insurable = _get_param('l10n_ca_qc_ei_max_insurable')
            box_24 = min(gross_total, ei_max_insurable) if ei_max_insurable else gross_total

            qpp_ympe = _get_param('l10n_ca_qc_qpp_ympe')
            qpp_exemption = _get_param('l10n_ca_qc_qpp_basic_exemption')
            if qpp_ympe and qpp_exemption:
                box_26 = max(min(gross_total, qpp_ympe) - qpp_exemption, 0)
            else:
                box_26 = gross_total

            qpip_max_insurable = _get_param('l10n_ca_qc_qpip_max_insurable')
            box_56 = min(gross_total, qpip_max_insurable) if qpip_max_insurable else gross_total

            slip.box_14 = gross_total
            slip.box_16 = _sum(['QPP_EE'])
            slip.box_17 = _sum(['QPP2_EE'])
            slip.box_18 = _sum(['EI_EE_QC'])
            slip.box_20 = _sum(['RPP_QC'])
            slip.box_22 = _sum(['FED_TAX_QC'])
            slip.box_24 = box_24
            slip.box_26 = box_26
            slip.box_44 = _sum(['UNION_QC'])
            slip.box_55 = _sum(['QPIP_EE'])
            slip.box_56 = box_56
            slip.state = 'generated'

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_export_xml(self):
        """Export T4 slips in CRA T619 XML format."""
        self.ensure_one()
        root = ET.Element('T619')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        # Submission info
        subm = ET.SubElement(root, 'submission')
        ET.SubElement(subm, 'tax_year').text = self.year
        ET.SubElement(subm, 'slp_cnt').text = '1'

        # T4 slip
        t4 = ET.SubElement(root, 'T4Slip')
        emp = self.employee_id
        ET.SubElement(t4, 'sin').text = emp.l10n_ca_qc_sin or emp.ssnid or ''
        ET.SubElement(t4, 'bn').text = self.company_id.vat or ''
        ET.SubElement(t4, 'empr_nm').text = self.company_id.name
        ET.SubElement(t4, 'empe_nm').text = emp.name
        ET.SubElement(t4, 'empe_addr').text = emp.private_street or ''

        for box, field in [
            ('empt_incamt', 'box_14'),
            ('cpp_qpp_cntrb_amt', 'box_16'),
            ('cpp2_qpp2_cntrb_amt', 'box_17'),
            ('ei_prm_amt', 'box_18'),
            ('rpp_cntrb_amt', 'box_20'),
            ('itx_ddctd_amt', 'box_22'),
            ('ei_insbr_erngs_amt', 'box_24'),
            ('cpp_qpp_ern_amt', 'box_26'),
            ('union_dues_amt', 'box_44'),
            ('ppip_prm_amt', 'box_55'),
            ('ppip_insbr_erngs_amt', 'box_56'),
        ]:
            val = getattr(self, field, 0.0)
            if val:
                ET.SubElement(t4, box).text = '%.2f' % val

        xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        filename = 'T4_%s_%s_%s.xml' % (
            self.year, self.employee_id.name.replace(' ', '_'), self.name
        )
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(xml_bytes),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/xml',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % attachment.id,
            'target': 'self',
        }


class L10nCaQcT4Summary(models.Model):
    _name = 'l10n_ca_qc.t4.summary'
    _description = 'T4 Summary'
    _order = 'year desc'

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self._default_name(),
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
            ('submitted', 'Submitted to CRA'),
        ],
        string="Status",
        default='draft',
        required=True,
        readonly=True,
    )
    slip_ids = fields.One2many(
        comodel_name='l10n_ca_qc.t4.slip',
        inverse_name='summary_id',
        string="T4 Slips",
    )
    total_employment_income = fields.Float(
        string="Total Employment Income (Box 14)",
        digits=(16, 2),
        compute='_compute_totals',
        store=True,
    )
    total_income_tax = fields.Float(
        string="Total Federal Income Tax Deducted (Box 22)",
        digits=(16, 2),
        compute='_compute_totals',
        store=True,
    )
    total_ei_premiums = fields.Float(
        string="Total EI Premiums (Box 18)",
        digits=(16, 2),
        compute='_compute_totals',
        store=True,
    )
    total_qpp_contributions = fields.Float(
        string="Total QPP Contributions (Box 16)",
        digits=(16, 2),
        compute='_compute_totals',
        store=True,
    )

    @api.model
    def _default_name(self):
        year = fields.Date.today().year
        return 'T4SUM-%s' % year

    @api.depends('slip_ids', 'slip_ids.box_14', 'slip_ids.box_22',
                 'slip_ids.box_18', 'slip_ids.box_16')
    def _compute_totals(self):
        for summary in self:
            summary.total_employment_income = sum(summary.slip_ids.mapped('box_14'))
            summary.total_income_tax = sum(summary.slip_ids.mapped('box_22'))
            summary.total_ei_premiums = sum(summary.slip_ids.mapped('box_18'))
            summary.total_qpp_contributions = sum(summary.slip_ids.mapped('box_16'))

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_generate_t4s(self):
        """Batch-generate a T4 slip for every employee who has confirmed payslips in the year."""
        self.ensure_one()
        date_from = '%s-01-01' % self.year
        date_to = '%s-12-31' % self.year
        payslips = self.env['hr.payslip'].search([
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['done', 'paid']),
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
        ])
        employee_ids = payslips.mapped('employee_id').ids
        for employee_id in employee_ids:
            existing = self.env['l10n_ca_qc.t4.slip'].search([
                ('employee_id', '=', employee_id),
                ('year', '=', self.year),
                ('company_id', '=', self.company_id.id),
            ], limit=1)
            if existing:
                t4_slip = existing
            else:
                t4_slip = self.env['l10n_ca_qc.t4.slip'].create({
                    'year': self.year,
                    'employee_id': employee_id,
                    'company_id': self.company_id.id,
                })
            t4_slip.action_generate()
            t4_slip.summary_id = self.id

    def action_export_xml(self):
        """Export all linked T4 slips as a single CRA T619 XML file."""
        self.ensure_one()
        root = ET.Element('T619')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        # Submission header
        subm = ET.SubElement(root, 'submission')
        ET.SubElement(subm, 'tax_year').text = self.year
        ET.SubElement(subm, 'slp_cnt').text = str(len(self.slip_ids))
        ET.SubElement(subm, 'rpt_tcd').text = 'O'

        # Transmitter / employer info
        employer_el = ET.SubElement(root, 'T4Summary')
        ET.SubElement(employer_el, 'bn').text = self.company_id.vat or ''
        ET.SubElement(employer_el, 'empr_nm').text = self.company_id.name or ''
        for slip in self.slip_ids:
            t4 = ET.SubElement(root, 'T4Slip')
            emp = slip.employee_id
            ET.SubElement(t4, 'sin').text = emp.l10n_ca_qc_sin or emp.ssnid or ''
            ET.SubElement(t4, 'bn').text = self.company_id.vat or ''
            ET.SubElement(t4, 'empr_nm').text = self.company_id.name or ''
            ET.SubElement(t4, 'empe_nm').text = emp.name or ''

            for box_tag, field_name in [
                ('empt_incamt', 'box_14'),
                ('cpp_qpp_cntrb_amt', 'box_16'),
                ('cpp2_qpp2_cntrb_amt', 'box_17'),
                ('ei_prm_amt', 'box_18'),
                ('rpp_cntrb_amt', 'box_20'),
                ('itx_ddctd_amt', 'box_22'),
                ('ei_insbr_erngs_amt', 'box_24'),
                ('cpp_qpp_ern_amt', 'box_26'),
                ('union_dues_amt', 'box_44'),
                ('ppip_prm_amt', 'box_55'),
                ('ppip_insbr_erngs_amt', 'box_56'),
            ]:
                val = getattr(slip, field_name, 0.0)
                if val:
                    ET.SubElement(t4, box_tag).text = '%.2f' % val

        xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        filename = 'T4_%s_%s.xml' % (
            self.year,
            (self.company_id.name or 'Company').replace(' ', '_'),
        )
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(xml_bytes),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/xml',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % attachment.id,
            'target': 'self',
        }
