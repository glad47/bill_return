# models/res_partner.py
from odoo import models, api, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_note_count = fields.Integer(string="Credit Notes", compute='_compute_credit_note_count')

 

    

    def action_vendor_credit_notes(self):
        return {
            'name': 'Vendor Credit Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [
                ('partner_id', '=', self.id),
                ('move_type', '=', 'in_refund'),
            ],
            'context': {
                'default_partner_id': self.id,
                'default_move_type': 'in_refund',
                'search_default_in_refund': 1,
            },
        }

    def _compute_credit_note_count(self):
        for partner in self:
            partner.credit_note_count = self.env['account.move'].search_count([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'in_refund')
            ])

