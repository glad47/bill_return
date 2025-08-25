from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    display_name = fields.Char(
        string="Display Name",
        compute='_compute_display_name',
        store=True
    )

    @api.depends('move_id.name', 'name')
    def _compute_display_name(self):
        for line in self:
            line.display_name = f"{line.move_id.name} - {line.name}"

    # bill_selector_id = fields.Many2one('account.move.bill.selector', string="Bill Selector")
