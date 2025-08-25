from odoo import models, fields, api

class BillResourceCenter(models.Model):
    _name = 'bill.resource.center'
    _description = 'Bill Resource Center'

    vendor_id = fields.Many2one('res.partner', string="Vendor")
    bill_ids = fields.One2many('account.move', 'resource_center_id', string="Bills")
    # total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount")
    # currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    # @api.depends('bill_ids.amount_total')
    # def _compute_total_amount(self):
    #     for rec in self:
    #         rec.total_amount = sum(rec.bill_ids.mapped('amount_total'))
    