# Part of MHC. See LICENSE file for full copyright and licensing details.

import base64
from lxml import etree

from odoo import api, fields, models


class L10nCaQcRl1Summary(models.Model):
    _name = 'l10n_ca_qc.rl1.summary'
    _description = 'Quebec RL-1 Summary (Relevé 1 Sommaire)'
    _order = 'year desc, company_id'

    name = fields.Char(
        string='Name',
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
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency',
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        string='Status',
        default='draft',
        required=True,
    )
    rl1_ids = fields.One2many(
        comodel_name='l10n_ca_qc.rl1.slip',
        inverse_name='summary_id',
        string='RL-1 Slips',
    )

    # Computed totals
    total_employees = fields.Integer(
        string='Total Employees',
        compute='_compute_totals',
        store=True,
    )
    total_box_a = fields.Float(
        string='Total Box A — Employment Income',
        compute='_compute_totals',
        store=True,
        digits=(16, 2),
    )
    total_box_b = fields.Float(
        string='Total Box B — QPP Contributions',
        compute='_compute_totals',
        store=True,
        digits=(16, 2),
    )
    total_box_c = fields.Float(
        string='Total Box C — EI Premiums',
        compute='_compute_totals',
        store=True,
        digits=(16, 2),
    )
    total_box_e = fields.Float(
        string='Total Box E — Quebec Income Tax Withheld',
        compute='_compute_totals',
        store=True,
        digits=(16, 2),
    )
    total_box_g = fields.Float(
        string='Total Box G — Union Dues',
        compute='_compute_totals',
        store=True,
        digits=(16, 2),
    )
    total_box_h = fields.Float(
        string='Total Box H — QPIP Premiums',
        compute='_compute_totals',
        store=True,
        digits=(16, 2),
    )

    # Transmitter / filer fields
    transmitter_ne = fields.Char(string="Employer NE (Numéro d'entreprise)")
    transmitter_name = fields.Char(string='Transmitter Name')
    contact_name = fields.Char(string='Contact Name')
    contact_phone = fields.Char(string='Contact Phone')
    contact_email = fields.Char(string='Contact Email')

    @api.depends('year', 'company_id')
    def _compute_name(self):
        for rec in self:
            company_name = rec.company_id.name or ''
            rec.name = 'RL-1 Summary - %s - %s' % (rec.year, company_name)

    @api.depends(
        'rl1_ids',
        'rl1_ids.box_a', 'rl1_ids.box_b', 'rl1_ids.box_c',
        'rl1_ids.box_e', 'rl1_ids.box_g', 'rl1_ids.box_h',
    )
    def _compute_totals(self):
        for rec in self:
            slips = rec.rl1_ids
            rec.total_employees = len(slips)
            rec.total_box_a = sum(slips.mapped('box_a'))
            rec.total_box_b = sum(slips.mapped('box_b'))
            rec.total_box_c = sum(slips.mapped('box_c'))
            rec.total_box_e = sum(slips.mapped('box_e'))
            rec.total_box_g = sum(slips.mapped('box_g'))
            rec.total_box_h = sum(slips.mapped('box_h'))

    def action_generate_rl1s(self):
        self.ensure_one()
        payslips = self.env['hr.payslip'].search([
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['done', 'paid']),
            ('date_from', '>=', '%s-01-01' % self.year),
            ('date_to', '<=', '%s-12-31' % self.year),
        ])
        employee_ids = payslips.mapped('employee_id').ids

        for employee_id in employee_ids:
            existing = self.env['l10n_ca_qc.rl1.slip'].search([
                ('employee_id', '=', employee_id),
                ('year', '=', self.year),
                ('company_id', '=', self.company_id.id),
            ], limit=1)
            if existing:
                slip = existing
            else:
                slip = self.env['l10n_ca_qc.rl1.slip'].create({
                    'year': self.year,
                    'employee_id': employee_id,
                    'company_id': self.company_id.id,
                })
            slip.action_generate()
            slip.summary_id = self.id

    def action_export_xml(self):
        self.ensure_one()
        root = etree.Element('Transmission')
        root.set('version', '2025')

        # Sommaire (Summary header)
        sommaire = etree.SubElement(root, 'Sommaire')
        self._add_xml_element(sommaire, 'AnneeFiscale', self.year)
        self._add_xml_element(sommaire, 'NomEmployeur', self.company_id.name or '')
        ne = self.transmitter_ne or ''
        self._add_xml_element(sommaire, 'NumeroEntreprise', ne)

        company = self.company_id
        if company.street:
            self._add_xml_element(sommaire, 'AdresseLigne1', company.street)
        if company.city:
            self._add_xml_element(sommaire, 'Ville', company.city)
        if company.state_id:
            self._add_xml_element(sommaire, 'Province', company.state_id.code)
        if company.zip:
            self._add_xml_element(sommaire, 'CodePostal', company.zip)

        self._add_xml_element(sommaire, 'NombreFeuillets', str(self.total_employees))
        self._add_xml_amount(sommaire, 'TotalBoxA', self.total_box_a)
        self._add_xml_amount(sommaire, 'TotalBoxB', self.total_box_b)
        self._add_xml_amount(sommaire, 'TotalBoxC', self.total_box_c)
        self._add_xml_amount(sommaire, 'TotalBoxE', self.total_box_e)
        self._add_xml_amount(sommaire, 'TotalBoxG', self.total_box_g)
        self._add_xml_amount(sommaire, 'TotalBoxH', self.total_box_h)

        if self.contact_name or self.contact_phone or self.contact_email:
            contact = etree.SubElement(sommaire, 'Responsable')
            self._add_xml_element(contact, 'Nom', self.contact_name)
            self._add_xml_element(contact, 'Telephone', self.contact_phone)
            self._add_xml_element(contact, 'Courriel', self.contact_email)

        # Individual RL-1 Slips
        for slip in self.rl1_ids:
            feuillet = etree.SubElement(root, 'FeuilletRL1')
            emp = slip.employee_id
            self._add_xml_element(feuillet, 'NomEmploye', emp.name or '')
            if emp.l10n_ca_qc_sin:
                self._add_xml_element(feuillet, 'NAS', emp.l10n_ca_qc_sin)
            self._add_xml_element(feuillet, 'Reference', slip.name)
            self._add_xml_amount(feuillet, 'CaseA', slip.box_a)
            self._add_xml_amount(feuillet, 'CaseB', slip.box_b)
            self._add_xml_amount(feuillet, 'CaseC', slip.box_c)
            self._add_xml_amount(feuillet, 'CaseD', slip.box_d)
            self._add_xml_amount(feuillet, 'CaseE', slip.box_e)
            self._add_xml_amount(feuillet, 'CaseG', slip.box_g)
            self._add_xml_amount(feuillet, 'CaseH', slip.box_h)
            self._add_xml_amount(feuillet, 'CaseI', slip.box_i)
            self._add_xml_amount(feuillet, 'CaseJ', slip.box_j)
            self._add_xml_amount(feuillet, 'CaseL', slip.box_l)
            if slip.box_o_amount:
                feuillet_o = etree.SubElement(feuillet, 'CaseO')
                feuillet_o.set('code', slip.box_o_code or '')
                feuillet_o.text = '%.2f' % slip.box_o_amount

        xml_bytes = etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        filename = 'RL1_%s_%s.xml' % (self.year, (self.company_id.name or 'Company').replace(' ', '_'))
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
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    def _add_xml_element(self, parent, tag, value):
        if value:
            elem = etree.SubElement(parent, tag)
            elem.text = str(value)

    def _add_xml_amount(self, parent, tag, amount):
        if amount:
            elem = etree.SubElement(parent, tag)
            elem.text = '%.2f' % amount

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})
