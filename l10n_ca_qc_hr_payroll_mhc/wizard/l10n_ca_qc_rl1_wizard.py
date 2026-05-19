# Part of MHC. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class L10nCaQcRl1Wizard(models.TransientModel):
    _name = 'l10n_ca_qc.rl1.wizard'
    _description = 'Generate RL-1 Slips Wizard'

    year = fields.Integer(
        string='Tax Year',
        required=True,
        default=lambda self: fields.Date.today().year,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    def action_generate(self):
        self.ensure_one()
        summary = self.env['l10n_ca_qc.rl1.summary'].create({
            'year': str(self.year),
            'company_id': self.company_id.id,
        })
        summary.action_generate_rl1s()
        return {
            'type': 'ir.actions.act_window',
            'name': 'RL-1 Summary',
            'res_model': 'l10n_ca_qc.rl1.summary',
            'res_id': summary.id,
            'view_mode': 'form',
            'target': 'current',
        }
