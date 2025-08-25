from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LinkedMoveLine(models.Model):
    _name = 'linked.move.line'
    _description = 'Linked Invoice Line Snapshot'

    # References
    move_id = fields.Many2one('account.move')  # Refund or parent document
    source_move_id = fields.Many2one('account.move')  # Original bill
    source_line_id = fields.Many2one('account.move.line')  # Original invoice line

    # Snapshot fields
    product_id = fields.Many2one('product.product')
    account_id = fields.Many2one('account.account')
    tax_ids = fields.Many2many('account.tax')
    discount = fields.Float()
    currency_id = fields.Many2one('res.currency')
    partner_id = fields.Many2one('res.partner')
    date = fields.Date()

    quantity = fields.Float(
    string="Quantity",
    compute="_compute_quantity",
    inverse="_inverse_quantity",
    store=True
    )




    name = fields.Char(
        string="Description",
        compute="_compute_name",
        inverse="_inverse_name",
        store=True
    )

    price_unit = fields.Float(
        string="Unit Price",
        compute="_compute_price_unit",
        store=True  # No inverse: read-only
    )

    return_amount = fields.Monetary(
        string="Return Amount",
        compute="_compute_return_amount",
        currency_field='currency_id',
        store=True
    )

    

    # Compute methods
    @api.depends('source_line_id')
    def _compute_quantity(self):
        for line in self:
            line.quantity = line.source_line_id.quantity if line.source_line_id else 0.0

    @api.depends('source_line_id')
    def _compute_price_unit(self):
        for line in self:
            line.price_unit = line.source_line_id.price_unit if line.source_line_id else 0.0

    @api.depends('source_line_id')
    def _compute_name(self):
        for line in self:
            line.name = line.source_line_id.name if line.source_line_id else ''

    @api.depends('quantity', 'price_unit')
    def _compute_return_amount(self):
        for line in self:
            line.return_amount = line.quantity * line.price_unit

    def _inverse_quantity(self):
        for line in self:
            if line.source_line_id:
                line.source_line_id.quantity = line.quantity  # Optional sync        

    # Inverse method for editable fields
    def _inverse_name(self):
        for line in self:
            if line.source_line_id:
                line.source_line_id.name = line.name

    # Constraint: quantity must not exceed original
    @api.constrains('quantity')
    def _check_quantity_not_exceed_original(self):
        for line in self:
            if line.source_line_id and line.quantity > line.source_line_id.quantity:
                raise ValidationError(
                    f"Return quantity ({line.quantity}) cannot exceed original quantity ({line.source_line_id.quantity})."
                )

    # Onchange: warn and correct excessive quantity
    @api.onchange('quantity')
    def _onchange_quantity_limit(self):
        for line in self:
            if line.source_line_id and line.quantity > line.source_line_id.quantity:
                line.quantity = line.source_line_id.quantity
                return {
                    'warning': {
                        'title': "Invalid Quantity",
                        'message': "You cannot return more than the original quantity."
                    }
                }
