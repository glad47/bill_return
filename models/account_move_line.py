from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    vendor_bills = fields.Many2one(
        'account.move',
        string="Vendor Bills",
        store=True
    )


    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                vendor_bills = self.env['account.move'].search([
                    ('move_type', '=', 'in_invoice'),
                    ('state', '=', 'posted'),
                    ('partner_id', '=', line.partner_id.id),
                    ('invoice_line_ids.product_id', 'in', [line.product_id.id])
                ])
                print(vendor_bills)
                return {
                    'domain': {
                        'vendor_bills': [('id', 'in', vendor_bills.ids)]
                    }
                }
            else:
                return {
                    'domain': {
                        'vendor_bills': []
                    }
                }


    @api.onchange('vendor_bills')
    def _onchange_vendor_bill(self):
        for line in self:
            if line.vendor_bills and line.product_id:
                # Find matching invoice lines in the selected bill
                matching_lines = line.vendor_bills.invoice_line_ids.filtered(
                    lambda l: l.product_id == line.product_id
                )
                if matching_lines:
                    # Use the first match (or customize logic if multiple)
                    match = matching_lines[0]
                    print(match)
                    line.quantity = match.quantity
                    line.price_unit = match.price_unit
                else:
                    line.quantity = 0.0
                    line.price_unit = 0.0
