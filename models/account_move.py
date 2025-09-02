from odoo import models, fields, api,Command

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    return_picking_ids = fields.Many2many(
        'stock.picking',
        string='Return Pickings',
        help='Pickings created to return goods for this bill',
        store=True
    )


    storage_id = fields.Many2one(
        'stock.location',
        string='Storage Location',
        store=True
    )


   
    return_picking_count = fields.Integer(
        string='Return Pickings',
        compute='_compute_return_picking_count'
    )

    def _compute_return_picking_count(self):
        for rec in self:
            rec.return_picking_count = len(rec.return_picking_ids)

  


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

    def action_post(self):
        moves_with_payments = self.filtered('payment_id')
        other_moves = self - moves_with_payments
        if moves_with_payments:
            moves_with_payments.payment_id.action_post()

        if other_moves:
            other_moves._post(soft=False)
            return_ids = []
            # Prepare new move values
            for line in other_moves.line_ids:
                for bill in line.vendor_bills:
                    if bill.invoice_origin:
                        po = self.env['purchase.order'].search([('name', '=', bill.invoice_origin)], limit=1)
                        if po:
                            oiginal_pk = {}
                            for pk in po.picking_ids:
                                if pk.origin == bill.invoice_origin:
                                    oiginal_pk = pk


                            incoming_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'),], limit=1)
                            location = self.env['stock.location'].search([
                                ('name', '=', 'Vendors')
                            ], limit=1)
                            picking = self.env['stock.picking'].create({
                                'partner_id' : other_moves.partner_id.id,
                                'picking_type_id': incoming_type.id,             
                                'location_id': oiginal_pk.location_id.id,            
                                'location_dest_id': other_moves.storage_id.id,     
                                'company_id': other_moves.company_id.id,              
                                'move_type': 'direct',                          
                                'immediate_transfer': False,                                                                   
                                'origin': 'Manual Picking Creation',             
                                                    
                            })

                            po.picking_ids += picking


                            for pk_line in oiginal_pk.move_line_ids:
                                self.env['stock.move.line'].create({
                                    'move_id': picking.move_ids.filtered(lambda m: m.product_id == pk_line.product_id).id,
                                    'picking_id': picking.id,
                                    'product_id': pk_line.product_id.id,
                                    'product_uom_id': pk_line.product_uom_id.id,
                                    'qty_done': pk_line.qty_done,
                                    'location_id': pk_line.location_id.id,
                                    'location_dest_id': pk_line.location_dest_id.id,
                                    'company_id': picking.company_id.id,
                                })
                                        
                            # Build product_return_moves from picking
                            print("setting info")

                            # print("################before#############")
                            # print(picking.read()[0])
                            # print("################after#############")
                            # picking.location_id =other_moves.storage_id

                            # print(picking.read()[0])
                            # print(other_moves.storage_id.read()[0])
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


                  
                           


                            

                           
                            # Create return wizard and trigger return
                            wizard = self.env['stock.return.picking'].with_context(active_id=picking.id).create({
                                'picking_id': picking.id,
                                'product_return_moves': return_lines,
                                'company_id': picking.company_id.id,
                                'location_id': location.id,
                            })
                        
                            return_action = wizard.create_returns()
                            

                            # print(move.location_id.id)
                            # print(other_moves.storage_id)
                        
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


                        else:
                            print(f"No picking found for PO: {bill.invoice_origin}")

            other_moves.return_picking_ids = [(6, 0, return_ids)]
        return False
       



   
    
    


   