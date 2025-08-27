from odoo import models, fields, api,Command

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


    def action_post(self):
        print("i am in my custome method -- overriding")

        moves_with_payments = self.filtered('payment_id')
        other_moves = self - moves_with_payments
        if moves_with_payments:
            moves_with_payments.payment_id.action_post()

        if other_moves:
            purchase_id = ""
            print("i am here ")
            # print("&&&&&&&&&&&&&&&&&&&&&&&&")
            # print(other_moves.read()[0])
            other_moves._post(soft=False)
            # Prepare new move values
            for line in other_moves.line_ids:
                for bill in line.vendor_bills:
                    print("xxxxxxxxxxxxx")
                    print(bill.invoice_origin)
                    if bill.invoice_origin:
                        po = self.env['purchase.order'].search([('name', '=', bill.invoice_origin)], limit=1)
                        print("################")
                        print(po.read()[0])
                    #     if po:
                    #         other_moves.write({
                    #             'purchase_id': po.id,
                    #             'invoice_origin': 'P00012',  # optional, for traceability
                    #             'purchase_order_count': 1,  # optional, if you're tracking count manually
                    #         })
                    #         pickings = po.picking_ids.filtered(lambda p: p.state == 'done')
                    #         print("**************pickings*************")
                    #         print(pickings)

                            
                            
                            
            #                 print(other_moves.read()[0])
            #                 other_moves._post(soft=False)
            #                 break
            

           
            # new_move.write({
            #     'purchase_order_count': 1,
            #     'invoice_origin': '',
            #     'ref': f"{other_moves.name or '/'} - Line {line.vendor_bills.name}",

            # })
            # if not other_moves.invoice_origin and other_moves.purchase_order_count == 0:
            #     id = other_moves.id
            #     first = True
            #     for line in other_moves.line_ids:
            #         if line.vendor_bills:
            #             invoice_name = line.vendor_bills.name

            #             # Prepare line-specific totals
            #             line_total = line.price_subtotal
            #             line_tax = line.tax_ids.compute_all(
            #                 line.price_unit,
            #                 currency=line.currency_id,
            #                 quantity=line.quantity,
            #                 product=line.product_id,
            #                 partner=line.partner_id
            #             )['total_included'] - line.price_subtotal

            #             # fallback_account_id = self.env['account.account'].search([
            #             #     ('user_type_id.type', '=', 'expense'),
            #             #     ('company_id', '=', self.env.company.id)
            #             # ], limit=1).id
                        
            #             invoice_line = Command.create({
            #                 'product_id': line.product_id.id,
            #                 'quantity': line.quantity,
            #                 'price_unit': line.price_unit,
            #                 'name': line.name,
            #                 'account_id': line.product_id.property_account_expense_id.id,
            #                 'price_subtotal': line_total,
            #             })

            #             tax_line = Command.create({
            #                 'name': 'Tax',
            #                 'account_id': line.tax_ids[0].invoice_repartition_line_ids.filtered(lambda r: r.repartition_type == 'tax').mapped('account_id')[0].id,
            #                 'debit': line_tax if line_tax > 0 else 0.0,
            #                 'credit': -line_tax if line_tax < 0 else 0.0,
            #             })

                        
                                                
                        

                        # if first:
                        #     new_move_vals.update({
                        #         'amount_total': line_total + line_tax,
                        #         'amount_tax': line_tax,
                        #         'invoice_origin': invoice_name,
                        #         'ref': f"{other_moves.name or '/'} - Line {line.vendor_bills.name}",
                        #         'invoice_line_ids': [invoice_line, tax_line],
                        #     })
                        #     print("***********@@@@@@@@1@@@@@@@@@****************")
                        #     new_move = self.env['account.move'].create(new_move_vals)
                        #     print(new_move)
                        #     new_move._post(soft=False)
                        #     first = False
                        # else:
                        #     new_move_vals.update({
                        #         'amount_total': line_total + line_tax,
                        #         'amount_tax': line_tax,
                        #         'invoice_origin': invoice_name,
                        #         'ref': f"{other_moves.name or '/'} - Line {line.vendor_bills.name}",
                        #         'invoice_line_ids': [invoice_line, tax_line],
                        #     })
                        #     new_move = self.env['account.move'].create(new_move_vals)
                        #     print("***********@@@@@@@@2@@@@@@@@@****************")
                        #     print(new_move)
                        #     new_move._post(soft=False)
                        

        # else: 
        #     res = other_moves._post(soft=False)
        #     print(res.read()[0])
        #     for move in res:
        #         if (
        #             move.move_type == 'in_refund'  # or 'in_refund' for vendor credit notes
        #             and move.state == 'posted'
        #         ):
        #             print("Confirmed credit note: %s", move.name)
        #             # 🔁 Your custom logic here
        #             #move._run_credit_note_hook()
        return False
       



   
    
    


   