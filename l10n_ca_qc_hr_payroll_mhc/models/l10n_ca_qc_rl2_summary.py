# Part of MHC. See LICENSE file for full copyright and licensing details.

import base64
from lxml import etree

from odoo import api, fields, models


class L10nCaQcRl2Summary(models.Model):
    _name = 'l10n_ca_qc.rl2.summary'
    _description = 'Quebec RL-2 Summary (Relevé 2 Sommaire)'
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
    rl2_ids = fields.One2many(
        comodel_name='l10n_ca_qc.rl2.slip',
        inverse_name='summary_id',
        string='RL-2 Slips',
    )

    # Computed totals
    total_recipients = fields.Integer(
        string='Total Recipients',
        compute='_compute_totals',
        store=True,
    )
    total_pension = fields.Monetary(
        string='Total Box A — Pension/Superannuation',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_lump_sum = fields.Monetary(
        string='Total Box B — Lump-Sum Payments',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_other = fields.Monetary(
        string='Total Box C — Other Income',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_tax = fields.Monetary(
        string='Total Box D — Quebec Income Tax Withheld',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_annuities = fields.Monetary(
        string='Total Box E — Annuities',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_self_employed = fields.Monetary(
        string='Total Box F — Self-Employed Commissions',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_fees = fields.Monetary(
        string='Total Box G — Fees for Services',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # Transmitter fields
    transmitter_ne = fields.Char(string="Employer NE (Numéro d'entreprise)")
    transmitter_name = fields.Char(string='Transmitter Name')
    contact_name = fields.Char(string='Contact Name')
    contact_phone = fields.Char(string='Contact Phone')
    contact_email = fields.Char(string='Contact Email')

    @api.depends('year', 'company_id')
    def _compute_name(self):
        for rec in self:
            company_name = rec.company_id.name or ''
            rec.name = 'RL-2 Summary - %s - %s' % (rec.year, company_name)

    @api.depends(
        'rl2_ids',
        'rl2_ids.box_a', 'rl2_ids.box_b', 'rl2_ids.box_c', 'rl2_ids.box_d',
        'rl2_ids.box_e', 'rl2_ids.box_f', 'rl2_ids.box_g',
    )
    def _compute_totals(self):
        for rec in self:
            slips = rec.rl2_ids
            rec.total_recipients = len(slips)
            rec.total_pension = sum(slips.mapped('box_a'))
            rec.total_lump_sum = sum(slips.mapped('box_b'))
            rec.total_other = sum(slips.mapped('box_c'))
            rec.total_tax = sum(slips.mapped('box_d'))
            rec.total_annuities = sum(slips.mapped('box_e'))
            rec.total_self_employed = sum(slips.mapped('box_f'))
            rec.total_fees = sum(slips.mapped('box_g'))

    def action_export_xml(self):
        self.ensure_one()
        root = etree.Element('Transmission')
        root.set('version', '2025')

        sommaire = etree.SubElement(root, 'Sommaire')
        self._add_xml_element(sommaire, 'AnneeFiscale', self.year)
        self._add_xml_element(sommaire, 'NomEmployeur', self.company_id.name or '')
        self._add_xml_element(sommaire, 'NumeroEntreprise', self.transmitter_ne or '')

        company = self.company_id
        if company.street:
            self._add_xml_element(sommaire, 'AdresseLigne1', company.street)
        if company.city:
            self._add_xml_element(sommaire, 'Ville', company.city)
        if company.state_id:
            self._add_xml_element(sommaire, 'Province', company.state_id.code)
        if company.zip:
            self._add_xml_element(sommaire, 'CodePostal', company.zip)

        self._add_xml_element(sommaire, 'NombreFeuillets', str(self.total_recipients))
        self._add_xml_amount(sommaire, 'TotalCaseA', self.total_pension)
        self._add_xml_amount(sommaire, 'TotalCaseB', self.total_lump_sum)
        self._add_xml_amount(sommaire, 'TotalCaseC', self.total_other)
        self._add_xml_amount(sommaire, 'TotalCaseD', self.total_tax)
        self._add_xml_amount(sommaire, 'TotalCaseE', self.total_annuities)
        self._add_xml_amount(sommaire, 'TotalCaseF', self.total_self_employed)
        self._add_xml_amount(sommaire, 'TotalCaseG', self.total_fees)

        if self.contact_name or self.contact_phone or self.contact_email:
            contact = etree.SubElement(sommaire, 'Responsable')
            self._add_xml_element(contact, 'Nom', self.contact_name)
            self._add_xml_element(contact, 'Telephone', self.contact_phone)
            self._add_xml_element(contact, 'Courriel', self.contact_email)

        for slip in self.rl2_ids:
            feuillet = etree.SubElement(root, 'FeuilletRL2')
            self._add_xml_element(feuillet, 'NomBeneficiaire', slip.recipient_name or '')
            if slip.recipient_sin:
                self._add_xml_element(feuillet, 'NAS', slip.recipient_sin)
            self._add_xml_element(feuillet, 'Reference', slip.name or '')
            self._add_xml_amount(feuillet, 'CaseA', slip.box_a)
            self._add_xml_amount(feuillet, 'CaseB', slip.box_b)
            self._add_xml_amount(feuillet, 'CaseC', slip.box_c)
            self._add_xml_amount(feuillet, 'CaseD', slip.box_d)
            self._add_xml_amount(feuillet, 'CaseE', slip.box_e)
            self._add_xml_amount(feuillet, 'CaseF', slip.box_f)
            self._add_xml_amount(feuillet, 'CaseG', slip.box_g)

        xml_bytes = etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        filename = 'RL2_%s_%s.xml' % (self.year, (self.company_id.name or 'Company').replace(' ', '_'))
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
