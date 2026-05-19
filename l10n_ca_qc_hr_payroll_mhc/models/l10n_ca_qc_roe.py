# Part of MHC. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import xml.etree.ElementTree as ET

from odoo import api, fields, models


class L10nCaQcRoeEarningsLine(models.Model):
    _name = 'l10n_ca_qc.roe.earnings.line'
    _description = 'ROE Insurable Earnings Line (Block 17)'
    _order = 'period_number'

    roe_id = fields.Many2one(
        comodel_name='l10n_ca_qc.roe',
        string="ROE",
        required=True,
        ondelete='cascade',
    )
    period_number = fields.Integer(string="Pay Period #", required=True)
    insurable_earnings = fields.Float(string="Insurable Earnings", digits=(16, 2))
    insurable_hours = fields.Float(string="Insurable Hours", digits=(16, 2))


class L10nCaQcRoe(models.Model):
    _name = 'l10n_ca_qc.roe'
    _description = 'Record of Employment (ROE)'
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
    serial_number = fields.Char(string="Serial Number")
    # Block dates
    first_day_worked = fields.Date(string="First Day Worked (Block 9)")
    last_day_paid = fields.Date(string="Last Day Paid (Block 10)")
    final_pay_period_end = fields.Date(string="Final Pay Period End (Block 11)")
    expected_recall_date = fields.Date(string="Expected Recall Date (Block 14)")
    # Block amounts
    total_insurable_hours = fields.Float(string="Total Insurable Hours (Block 12)", digits=(16, 2))
    total_insurable_earnings = fields.Float(string="Total Insurable Earnings (Block 13)", digits=(16, 2))
    vacation_pay = fields.Float(string="Vacation Pay (Block 15A)", digits=(16, 2))
    other_monies = fields.Float(string="Other Monies (Block 15B)", digits=(16, 2))
    # Block 16 — Reason for issuing ROE
    reason_code = fields.Selection(
        selection=[
            ('A', 'A — Shortage of Work'),
            ('B', 'B — Strike/Lockout'),
            ('C', 'C — Return to School'),
            ('D', 'D — Illness/Injury'),
            ('E', 'E — Quit'),
            ('F', 'F — Maternity'),
            ('G', 'G — Retirement'),
            ('H', 'H — Work Sharing'),
            ('J', 'J — Apprentice Training'),
            ('K', 'K — Other'),
            ('M', 'M — Dismissal'),
            ('N', 'N — Leave of Absence'),
            ('P', 'P — Parental'),
            ('Z', 'Z — Compassionate Care'),
        ],
        string="Reason Code (Block 16)",
    )
    reason_description = fields.Char(string="Reason Description")
    pay_period_type = fields.Selection(
        selection=[
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-Weekly'),
            ('semi_monthly', 'Semi-Monthly'),
            ('monthly', 'Monthly'),
        ],
        string="Pay Period Type",
    )
    insurable_earnings_line_ids = fields.One2many(
        comodel_name='l10n_ca_qc.roe.earnings.line',
        inverse_name='roe_id',
        string="Earnings by Period (Block 17)",
    )

    @api.model
    def _default_name(self):
        year = fields.Date.today().year
        seq = self.env['ir.sequence'].next_by_code('l10n_ca_qc.roe') or '001'
        return 'ROE-%s-%s' % (year, seq)

    def action_generate(self):
        for roe in self:
            date_from = roe.first_day_worked
            date_to = roe.last_day_paid
            domain = [
                ('employee_id', '=', roe.employee_id.id),
                ('state', 'in', ['done', 'paid']),
            ]
            if date_from:
                domain.append(('date_from', '>=', date_from))
            if date_to:
                domain.append(('date_to', '<=', date_to))

            payslips = self.env['hr.payslip'].search(domain, order='date_from')

            # Total insurable earnings from GROSS_QC lines
            lines = payslips.mapped('line_ids')
            roe.total_insurable_earnings = sum(
                l.total for l in lines if l.code == 'GROSS_QC'
            )

            # Total insurable hours from work entries
            work_entries = self.env['hr.work.entry'].search([
                ('employee_id', '=', roe.employee_id.id),
                ('date_start', '>=', datetime.datetime.combine(date_from, datetime.time.min) if date_from else False,),
                ('date_stop', '<=', datetime.datetime.combine(date_to, datetime.time.max) if date_to else False,),
                ('state', '=', 'validated'),
            ]) if date_from and date_to else self.env['hr.work.entry']
            roe.total_insurable_hours = sum(
                (we.date_stop - we.date_start).total_seconds() / 3600
                for we in work_entries
            )

            # Vacation pay from payslip inputs
            vacation_inputs = payslips.mapped('input_line_ids').filtered(
                lambda i: i.code == 'VACATION_PAY'
            )
            roe.vacation_pay = sum(i.amount for i in vacation_inputs)

            # Earnings lines per pay period
            roe.insurable_earnings_line_ids.unlink()
            period_lines = []
            for period_num, payslip in enumerate(payslips, start=1):
                gross = sum(
                    l.total for l in payslip.line_ids if l.code == 'GROSS_QC'
                )
                hours = sum(
                    (we.date_stop - we.date_start).total_seconds() / 3600
                    for we in self.env['hr.work.entry'].search([
                        ('employee_id', '=', roe.employee_id.id),
                        ('date_start', '>=', datetime.datetime.combine(payslip.date_from, datetime.time.min)),
                        ('date_stop', '<=', datetime.datetime.combine(payslip.date_to, datetime.time.max)),
                        ('state', '=', 'validated'),
                    ])
                )
                period_lines.append({
                    'roe_id': roe.id,
                    'period_number': period_num,
                    'insurable_earnings': gross,
                    'insurable_hours': hours,
                })
            self.env['l10n_ca_qc.roe.earnings.line'].create(period_lines)
            roe.state = 'generated'

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_export_xml(self):
        """Export ROE in Service Canada ROE Web XML format."""
        self.ensure_one()
        root = ET.Element('ROEWeb')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        # Block 1 — Serial Number
        ET.SubElement(root, 'SerialNumber').text = self.serial_number or ''

        # Block 2 — Employer Info
        employer = ET.SubElement(root, 'Employer')
        ET.SubElement(employer, 'Name').text = self.company_id.name
        ET.SubElement(employer, 'PayrollRefNumber').text = self.company_id.vat or ''
        ET.SubElement(employer, 'Address').text = ', '.join(filter(None, [
            self.company_id.street,
            self.company_id.city,
            self.company_id.state_id.name if self.company_id.state_id else '',
            self.company_id.zip,
        ]))

        # Block 4 — Employee Info
        employee = ET.SubElement(root, 'Employee')
        emp = self.employee_id
        ET.SubElement(employee, 'SIN').text = emp.l10n_ca_qc_sin or emp.ssnid or ''
        ET.SubElement(employee, 'Name').text = emp.name
        ET.SubElement(employee, 'Address').text = emp.private_street or ''

        # Block 6 — Pay Period Type
        ET.SubElement(root, 'PayPeriodType').text = self.pay_period_type or ''

        # Block 9-11 — Dates
        if self.first_day_worked:
            ET.SubElement(root, 'FirstDayWorked').text = str(self.first_day_worked)
        if self.last_day_paid:
            ET.SubElement(root, 'LastDayPaid').text = str(self.last_day_paid)
        if self.final_pay_period_end:
            ET.SubElement(root, 'FinalPayPeriodEndDate').text = str(self.final_pay_period_end)

        # Block 12-13 — Totals
        ET.SubElement(root, 'TotalInsurableHours').text = '%.2f' % (self.total_insurable_hours or 0)
        ET.SubElement(root, 'TotalInsurableEarnings').text = '%.2f' % (self.total_insurable_earnings or 0)

        # Block 14 — Expected Recall Date
        if self.expected_recall_date:
            ET.SubElement(root, 'ExpectedRecallDate').text = str(self.expected_recall_date)

        # Block 15A — Vacation Pay
        if self.vacation_pay:
            ET.SubElement(root, 'VacationPay').text = '%.2f' % self.vacation_pay

        # Block 15B — Other Monies
        if self.other_monies:
            ET.SubElement(root, 'OtherMonies').text = '%.2f' % self.other_monies

        # Block 16 — Reason Code
        if self.reason_code:
            ET.SubElement(root, 'ReasonCode').text = self.reason_code
        if self.reason_description:
            ET.SubElement(root, 'ReasonDescription').text = self.reason_description

        # Block 17 — Earnings by Period
        if self.insurable_earnings_line_ids:
            block17 = ET.SubElement(root, 'EarningsByPeriod')
            for line in self.insurable_earnings_line_ids.sorted('period_number'):
                period_el = ET.SubElement(block17, 'Period')
                ET.SubElement(period_el, 'PeriodNumber').text = str(line.period_number)
                ET.SubElement(period_el, 'InsurableEarnings').text = '%.2f' % line.insurable_earnings
                ET.SubElement(period_el, 'InsurableHours').text = '%.2f' % line.insurable_hours

        xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        filename = 'ROE_%s_%s.xml' % (
            self.employee_id.name.replace(' ', '_'), self.name
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
