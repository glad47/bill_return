from odoo import models, fields, api

class AccountMoveBillSelector(models.Model):
    _name = 'account.move.bill.selector'
    _description = 'Vendor Bill Selector'

    move_id = fields.Many2one('account.move', string="Parent Move")
    bill_id = fields.Many2one('account.move', string="Vendor Bill", domain="[('move_type', '=', 'in_invoice')]")
    bill_date = fields.Date(related='bill_id.invoice_date', store=True)
    amount_total = fields.Monetary(related='bill_id.amount_total', currency_field='currency_id', store=True)
    currency_id = fields.Many2one(related='bill_id.currency_id', store=True)
    # invoice_line_ids = fields.One2many('account.move.line', 'bill_selector_id', string="Invoice Lines")
