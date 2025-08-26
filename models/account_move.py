from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    vendor_purchase_bill_ids = fields.Many2many(
        'account.move',
        'account_move_vendor_purchase_rel',  # optional: custom relation table name
        'move_id', 'bill_id',  
        string="Related Vendor Bills",
        domain="[('state', '=', 'posted'), ('move_type', '=', 'in_invoice'), ('partner_id', '=', partner_id)]"
    )


    product_ids = fields.Many2many(
        'product.product',
        string="Products in Bill",
        compute='_compute_product_ids',
        store=True
    )

    @api.depends('invoice_line_ids.product_id')
    def _compute_product_ids(self):
        for move in self:
            move.product_ids = move.invoice_line_ids.mapped('product_id')



   
    
    


   