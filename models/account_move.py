from odoo import models, fields, api,Command
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    return_picking_ids = fields.Many2many(
        'stock.picking',
        'account_move_return_picking_rel',
        'move_id',
        'picking_id',
        string='Return Pickings'
    )



    return_picking_count = fields.Integer(
        string='Return Pickings',
        compute='_compute_return_picking_count'
    )

    storage_id = fields.Many2one(
        'stock.location',
        string='Storage Location',
        domain=lambda self: [('id', 'in', self._get_allowed_storage_ids())],
        default=lambda self: self._get_default_storage_id(),
        store=True
    )

    transfer_picking_ids = fields.Many2many(
        'stock.picking',
        'account_move_transfer_picking_rel',
        'move_id',
        'picking_id',
        string='Transfer Pickings'
    )

    transfer_picking_count = fields.Integer(
        string='Return Pickings',
        compute='_compute_transfer_picking_count'
    )


   
    

    def _compute_return_picking_count(self):
        for rec in self:
            rec.return_picking_count = len(rec.return_picking_ids)


    def _compute_transfer_picking_count(self):
        for rec in self:
            rec.transfer_picking_count = len(rec.transfer_picking_ids)        
    


    def _get_allowed_storage_ids(self):
        config = self.env['bill.return.config'].search([], limit=1)
        return config.location_ids.ids if config else []

    def _get_default_storage_id(self):
        config = self.env['bill.return.config'].search([], limit=1)
        return config.default_location_id.id if config and config.default_location_id else False

    # def _get_default_transit_location_id(self):
    #     config = self.env['bill.return.config'].search([], limit=1)
    #     return config.default_intermediate_location_id.id if config and config.default_intermediate_location_id else False




    def action_view_return_pickings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receipt',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.return_picking_ids.ids)],
            'context': {'default_origin': self.name},
        }
    
    def action_view_transfer_pickings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receipt',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.transfer_picking_ids.ids)],
            'context': {'default_origin': self.name},
        }
    

    @api.onchange('storage_id')
    def _onchange_storage_id_update_qty(self):
        location = self.storage_id
        for line in self.invoice_line_ids:
            if line.product_id and location:
                line.compute_qty_allowed()


    def action_post(self):
        moves_with_payments = self.filtered('payment_id')
        other_moves = self - moves_with_payments
        if moves_with_payments:
            moves_with_payments.payment_id.action_post()

        if other_moves:
            other_moves._post(soft=False)
            return_ids = []
            transfer_ids = []
            location = self.storage_id
            if not location:
                return

            
            # Prepare new move values
            for line in other_moves.line_ids:
                for bill in line.vendor_bills:
                    if bill.invoice_origin:
                        invalid_products = []

                        for line in self.invoice_line_ids:
                            if line.product_id:
                                line.compute_qty_allowed()
                                if line.qty_allowed == 0:
                                    invalid_products.append(line.product_id.display_name)

                        if invalid_products:
                            raise ValidationError(
                                "The following products have zero allowed quantity at location '%s':\n- %s" % (
                                    location.complete_name,
                                    "\n- ".join(invalid_products)
                                )
                            )
                        config = self.env['bill.return.config'].search([], limit=1)
                        if not config or not config.default_location_id:
                            raise ValidationError("You need to config Bill Return first, Configuration is missing.")
                        po = self.env['purchase.order'].search([('name', '=', bill.invoice_origin)], limit=1)
                        if po and po.picking_ids:
                           
                            picking = {}
                            for pk in po.picking_ids:
                                if pk.origin == bill.invoice_origin:
                                    picking = pk
                                 
                            # Build product_return_moves from picking
                            return_lines = []
                            for move in picking.move_line_ids:
                                # if move.product_id.type != 'product':
                                #     continue
                                if move.product_id.id != line.product_id.id:
                                    continue    
                                return_lines.append((0, 0, {
                                    'product_id': line.product_id.id,
                                    'quantity': line.quantity,
                                    'move_id': move.move_id.sudo().id,
                                    'to_refund': True,
                                }))


                            location = self.env['stock.location'].search([
                                            ('name', '=', 'Vendors')
                            ], limit=1) 

                            # Create return wizard and trigger return
                            wizard = self.env['stock.return.picking'].with_context(active_id=picking.id).create({
                                'picking_id': picking.id,
                                'product_return_moves': return_lines,
                                'company_id': picking.company_id.id,
                                'location_id': location.id,
                            })
                        
                            return_action = wizard.create_returns()
                            
                        
                            if return_action and 'res_id' in return_action:
                                return_picking = self.env['stock.picking'].browse(return_action['res_id'])
                                return_ids.append(return_picking.id)

                                # Set quantity_done for each move line
                                for move in return_picking.move_ids:
                                    self.env['stock.move.line'].create({
                                            'move_id': move.id,  # the move inside return_picking
                                            'picking_id': return_picking.id,
                                            'product_id': move.product_id.id,
                                            'product_uom_id': move.product_uom.id,
                                            'location_id':  move.location_id.id,       # reverse: from WH/Stock
                                            'location_dest_id':move.location_dest_id.id,       # reverse: to Vendors
                                            'company_id': move.company_id.id,
                                            'qty_done': line.quantity,                                 # e.g. 50.0
                                        })
                                        
                                return_picking.action_confirm()
                                return_picking.action_assign()
                                
                                # Validate the picking (final step)
                                return_picking.button_validate()
                                
                                # dont allow
                                if po.invoice_status != 'invoiced':
                                    po.invoice_status = 'invoiced'

                                for po_line in po.order_line:
                                    if po_line.product_id.id == move.product_id.id:
                                        if po_line.qty_invoiced > 0:
                                            new_qty = po_line.qty_invoiced - line.quantity
                                            po_line.qty_invoiced = new_qty
                                        else:
                                            new_qty = po_line.qty_invoiced + (line.quantity * -1)
                                            po_line.qty_invoiced = new_qty   

                                # Link the bill to the PO
                                if other_moves.id not in po.linked_batch_bill_ids.ids:
                                    po.write({'linked_batch_bill_ids': [(4, other_moves.id)]})   
                                

                                if picking.location_dest_id.complete_name != other_moves.storage_id.complete_name:
                                    
                                   
                                    

                                    # Find the internal picking type mapped to the destination location
                                    picking_type_line = config.location_picking_type_map_ids.filtered(
                                        lambda line: line.location_id.id == picking.location_dest_id.id
                                    )



                                    

                                    if not picking_type_line:
                                        raise ValidationError(
                                            f"No internal picking type configured for location: {picking.location_dest_id.complete_name}"
                                        )

                                    # Find the vendor mapped to the destination location
                                    vendor_line = config.location_vendor_map_ids.filtered(
                                        lambda line: line.location_id.id == picking.location_dest_id.id
                                    )

                                    if not vendor_line:
                                        raise ValidationError(
                                            f"No vendor configured for location: {picking.location_dest_id.complete_name}"
                                        )

                                    transfer_picking = self.env['stock.picking'].create({
                                        'partner_id': vendor_line.vendor_id.id,
                                        'picking_type_id': picking_type_line.picking_type_id.id,
                                        'location_id': other_moves.storage_id.id,
                                        'location_dest_id': picking.location_dest_id.id,
                                        'move_type': 'direct',
                                        'company_id': picking.company_id.id,
                                    })

                                    new_transfer_move = self.env['stock.move'].create({
                                        'name': transfer_picking.name,
                                        'product_id': line.product_id.id,
                                        'product_uom_qty': line.quantity,
                                        'product_uom': move.product_uom.id,
                                        'picking_id': transfer_picking.id,
                                        'location_id': transfer_picking.location_id.id,
                                        'location_dest_id': transfer_picking.location_dest_id.id,
                                        'partner_id': transfer_picking.partner_id.id,
                                        'picking_type_id': transfer_picking.picking_type_id.id,
                                        'company_id': transfer_picking.company_id.id,
                                        'state': 'draft',
                                    })

                                    self.env['stock.move.line'].create({
                                        'picking_id': transfer_picking.id,
                                        'move_id': new_transfer_move.id,
                                        'company_id': transfer_picking.company_id.id,
                                        'product_id': new_transfer_move.product_id.id,
                                        'product_uom_id': new_transfer_move.product_uom.id,
                                        'location_id': new_transfer_move.location_id.id,
                                        'location_dest_id': new_transfer_move.location_dest_id.id,
                                        'qty_done': new_transfer_move.product_uom_qty,  # or line.quantity if you want to override
                                    })


                                    


                                    transfer_picking.action_confirm()
                                    transfer_picking.action_assign()
                                    
                                    # Validate the picking (final step)
                                    transfer_picking.button_validate()
                                    
                                    transfer_ids.append(transfer_picking.id)
                                    if other_moves.id not in po.linked_picking_ids.ids:
                                        po.write({'linked_picking_ids': [(4, transfer_picking.id)]})



                                    
                                    print(f"Created receipt picking: {transfer_picking.name}")
                                

                                    

                                    
  



                        else:
                            print(f"No picking found for PO: {bill.invoice_origin}")
            if len(return_ids) > 0 :
                other_moves.return_picking_ids = [(6, 0, return_ids)]
            if len(transfer_ids) > 0 :
                other_moves.transfer_picking_ids = [(6, 0, transfer_ids)]
        return False
       



   
    
    


   