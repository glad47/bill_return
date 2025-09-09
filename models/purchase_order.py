
from odoo import models, fields, api,Command
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    linked_batch_bill_ids = fields.Many2many(
        'account.move',
        string='Linked Batch Vendor Bills',
        relation='purchase_order_linked_batch_bill_rel',
        column1='purchase_order_id',
        column2='account_move_id',
        store=True,
    )

    linked_picking_ids = fields.Many2many(
        'stock.picking',
        string='Linked Stock Movement',
        relation='purchase_order_linked_picking_rel',  # ← unique relation table
        column1='purchase_order_id',
        column2='picking_id',
        store=True,
    )


    linked_batch_bill_count = fields.Integer(
        string='Batch Bill Count',
        compute='_compute_linked_batch_bill_count',
    )

    linked_stock_movement_count = fields.Integer(
        string='Stock Movement Count',
        compute='_compute_linked_stock_movement_count',
    )



    @api.depends('linked_batch_bill_ids')
    def _compute_linked_batch_bill_count(self):
        for record in self:
            record.linked_batch_bill_count = len(record.linked_batch_bill_ids)


    @api.depends('linked_picking_ids')
    def _compute_linked_stock_movement_count(self):
        for record in self:
            record.linked_stock_movement_count = len(record.linked_picking_ids)        


    def action_open_linked_batch_bills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Linked Vendor Bills',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.linked_batch_bill_ids.ids)],
            'context': {'create': False},
        }
    
    def action_open_stock_movement(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Linked Stock Movement',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.linked_picking_ids.ids)],
            'context': {'create': False},
        }
        


