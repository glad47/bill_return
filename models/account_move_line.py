from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    vendor_bills = fields.Many2one(
        'account.move',
        string="Vendor Bills",
        store=True
    )

    qty_allowed = fields.Float(
        string="Allowed Quantity",
        compute="_compute_qty_allowed",
        readonly=True,
        store=True,
    )

    location_name = fields.Char(
        string="Location",
        compute="_compute_location_name",
        store=True
    )

    @api.depends('vendor_bills')
    def _compute_location_name(self):
        for line in self:
            line.location_name = self._get_main_picking_location_name(line.vendor_bills)





    @api.onchange('quantity')
    def _onchange_quantity(self):
        for line in self:
            if line.qty_allowed and line.quantity > line.qty_allowed:
                line.quantity = line.qty_allowed
                return {
                    'warning': {
                        'title': "Quantity Exceeded",
                        'message': f"You cannot set quantity greater than allowed ({line.qty_allowed})."
                    }
                }




    @api.depends('product_id', 'vendor_bills', 'partner_id')
    def _compute_qty_allowed(self):
        for line in self:
            line.qty_allowed = 0.0
            if not line.product_id or not line.partner_id or not line.vendor_bills:
                continue
            qty_allowed, _ = self._get_qty_allowed_and_eligible_bills(line)
            # line.location_name = self._get_main_picking_location_name(line.vendor_bills)
            # print("cccccxxxxxxxxxxxxccccccccccccxxxxxxxxxxxxxxxxxxxxcccccc")
            # print(line.location_name)
            line.qty_allowed = qty_allowed



    def _get_qty_allowed_and_eligible_bills(self, line):
        qty_allowed = 0.0
        eligible_bills = []

        vendor_bills = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('partner_id', '=', line.partner_id.id),
            ('invoice_line_ids.product_id', '=', line.product_id.id)
        ])

        for bill in vendor_bills:
            po = self.env['purchase.order'].search([
                ('name', '=', bill.invoice_origin)
            ], limit=1)

            if not po or not po.picking_ids:
                continue

            origin_pk = next((pk for pk in po.picking_ids if pk.origin == bill.invoice_origin), None)
            if not origin_pk:
                continue

            qty_total = sum(
                move.qty_done
                for pk in po.picking_ids
                if pk.origin != bill.invoice_origin
                for move in pk.move_line_ids
                if move.product_id.id == line.product_id.id
            )

            print("...........qty_total..........")
            print(qty_total)

            qty_origin = sum(
                move.qty_done
                for move in origin_pk.move_line_ids
                if move.product_id.id == line.product_id.id
            )


            print("...........qty_origin..........")
            print(qty_origin)

            diff = qty_origin - qty_total
            print("*********diff********")
            print(diff)
            if diff > 0:
                if bill == line.vendor_bills:

                    # Always compute current storage from all PO pickings
                    
                    stock_qty = self._get_stock_in_location(line.product_id, origin_pk.location_dest_id)
                    print("0000000000000000000000000000000000000000000000000000000000000000000000")
                    print(origin_pk.location_dest_id)
                    print(stock_qty)
                    diff2 = 0
                    if stock_qty > 0: 
                        diff2 = stock_qty - diff
                        if diff2 >= 0:
                            qty_allowed = diff
                    else:
                        qty_allowed = 0 
                    
                eligible_bills.append(bill.id)

        return qty_allowed, eligible_bills


    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id or not line.partner_id:
                return {'domain': {'vendor_bills': []}}

            _, eligible_bills = self._get_qty_allowed_and_eligible_bills(line)
            return {
                'domain': {
                    'vendor_bills': [('id', 'in', eligible_bills)]
                }
            }
        

    def _get_stock_in_location(self, product_id, location_id):
        # print(product_id)
        # print(location_id)
        domain = [
            ('product_id', '=', product_id.id),
            ('location_id', '=', location_id.id)
        ]
        quants = self.env['stock.quant'].search(domain)
        total_qty = sum(quant.quantity for quant in quants)
        return total_qty

    






    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     for line in self:
    #         if line.product_id:
    #             vendor_bills = self.env['account.move'].search([
    #                 ('move_type', '=', 'in_invoice'),
    #                 ('state', '=', 'posted'),
    #                 ('partner_id', '=', line.partner_id.id),
    #                 ('invoice_line_ids.product_id', 'in', [line.product_id.id])
    #             ])
    #             print(vendor_bills)
    #             return {
    #                 'domain': {
    #                     'vendor_bills': [('id', 'in', vendor_bills.ids)]
    #                 }
    #             }
    #         else:
    #             return {
    #                 'domain': {
    #                     'vendor_bills': []
    #                 }
    #             }


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
                    # line.quantity = match.quantity
                    line.price_unit = match.price_unit
                else:
                    # line.quantity = 0.0
                    line.price_unit = 0.0


    def _get_main_picking_location_name(self, bill):
        if not bill.invoice_origin:
            return False

        po = self.env['purchase.order'].search([('name', '=', bill.invoice_origin)], limit=1)
       
        print(po.read()[0])
        if not po or not po.picking_ids:
            return False

        for pk in po.picking_ids:
            if pk.origin == bill.invoice_origin:
                return pk.location_dest_id.complete_name

        return False
                
