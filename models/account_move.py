from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    vendor_purchase_bill_ids = fields.Many2many(
        'account.move',
        'account_move_vendor_purchase_rel',  # optional: custom relation table name
        'move_id', 'bill_id',  
        string="Related Vendor Bills",
        domain="[ ('state', '=', 'posted'), ('move_type', '=', 'in_invoice'), ('partner_id', '=', partner_id)]"
    )

    linked_invoice_line_ids = fields.One2many(
        'account.move.line',
        'move_id',
        string="Linked Invoice Lines",
    )


    # @api.onchange('vendor_purchase_bill_ids')
    # def _compute_linked_invoice_lines(self):
    #     all_lines = self.env['account.move.line']
    #     for bill in self.vendor_purchase_bill_ids:
    #         all_lines |= bill.invoice_line_ids
    #     self.linked_invoice_line_ids = all_lines

    # related_invoice_lines = fields.One2many(
    #     'account.move.line',
    #     compute='_compute_related_invoice_lines',
    #     string="Editable Bill Lines",
    #     store=False
    # )


   

    # bill_line_map = fields.Json(
    #         string="Bill to Lines Map",
    #         compute="_compute_bill_line_map",
    #         store=False
    #     )
    

    @api.onchange('vendor_purchase_bill_ids')
    def _onchange_update_line_names(self):
        for bill in self.vendor_purchase_bill_ids:
            for line in bill.line_ids:
                line.name = f"{bill.name}"
    


    # @api.depends('vendor_purchase_bill_ids')
    # def _compute_related_invoice_lines(self):
    #     for move in self:
    #         print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    #         print(move.read()[0])
            # lines = self.env['account.move.line'].search([
            #     ('move_id', 'in', move.vendor_purchase_bill_ids.ids)
            # ])
            # print(lines)
            # move.related_invoice_lines = lines


    # @api.depends('vendor_purchase_bill_ids')
    # def _compute_bill_line_map(self):
    #     for move in self:
    #         mapping = {}
    #         for bill in move.vendor_purchase_bill_ids:
    #             mapping[bill.id] = [{
    #                 'line_id': line.id,
    #                 'name': line.name,
    #                 'product': line.product_id.name,
    #                 'quantity': line.quantity,
    #                 'price_unit': line.price_unit,
    #                 'account': line.account_id.name,
    #             } for line in bill.invoice_line_ids]
    #         move.bill_line_map = mapping

    

    # def _compute_partner_purchase_bill_ids(self):
    #     for move in self:
    #         move.vendor_purchase_bill_ids = move.partner_id.purchase_bill_ids
                
            


    # vendor_id = fields.Many2one(
    #     'res.partner',
    #     string="Vendor",
    #     compute='_compute_vendor_id',
    #     store=True
    # )

    # related_vendor_bills = fields.One2many(
    #     'account.move',
    #     'bills_id',
    #     string="Other Bills from Same Vendor",
    #     compute='_compute_related_vendor_bills',
    #     store=False
    # )

    # @api.model
    # def _compute_vendor_id(self):
    #     for move in self:
    #         move.vendor_id = move.partner_id
    


    # def compute_related_vendor_bills(self):
    #     print("i am outside &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    #     for move in self:
    #         print("i am inside &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    #         print(move)
    #         if move.partner_id:
    #             bills = self.env['account.move'].search([
    #                 ('partner_id', '=', move.partner_id.id),
    #             ])
    #             # print("***************************************************************")
    #             # print(f"Total bills found: {len(bills)}")
    #             # for bill_data in bills.read():
    #             #     print("\n--- Bill Details ---")
    #             #     for key, value in bill_data.items():
    #             #         print(f"{key}: {value}")
    #             selectors = []
    #             for bill in bills:
    #                 if bill.move_type == 'in_invoice':
    #                     # selector = self.env['account.move.bill.selector'].create({
    #                     #     'move_id': move.id,
    #                     #     'bill_id': bill.id,
    #                     # })
    #                     # for line in bill.invoice_line_ids:
    #                     #     self.env['account.move.line'].create({
    #                     #         'move_id': move.id,  # ← This is the fix
    #                     #         'product_id': line.product_id.id,
    #                     #         'quantity': line.quantity,
    #                     #         'price_unit': line.price_unit,
    #                     #         'name': line.name,
    #                     #         'account_id': line.account_id.id,
    #                     #     })

    #                     selectors.append(bill)
    #             move.related_vendor_bills = [(6, 0, selectors)]
    # @api.model
    # def _compute_related_vendor_bills(self):
    #     print("i am outside &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    #     for move in self:
    #         print("i am inside &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    #         print(move)
    #         if move.partner_id:
    #             bills = self.env['account.move'].search([
    #                 ('partner_id', '=', move.partner_id.id),
    #             ])
    #             print("***************************************************************")
    #             for bill_data in bills.read():
    #                 print("\n--- Bill Details ---")
    #                 for key, value in bill_data.items():
    #                     print(f"{key}: {value}")
    #             selectors = []
    #             for bill in bills:
    #                 if bill.move_type == 'in_invoice':
    #                     # selector = self.env['account.move.bill.selector'].create({
    #                     #     'move_id': move.id,
    #                     #     'bill_id': bill.id,
    #                     # })
    #                     # for line in bill.invoice_line_ids:
    #                     #     self.env['account.move.line'].create({
    #                     #         'move_id': move.id,  # ← This is the fix
    #                     #         'product_id': line.product_id.id,
    #                     #         'quantity': line.quantity,
    #                     #         'price_unit': line.price_unit,
    #                     #         'name': line.name,
    #                     #         'account_id': line.account_id.id,
    #                     #     })

    #                     selectors.append(bill)
    #                 # selectors.append(selector.id)
    #             move.related_vendor_bills = [(6, 0, selectors)]
