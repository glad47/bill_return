from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BillReturnLocationVendor(models.Model):
    _name = 'bill.return.location.vendor'
    _description = 'Location-Vendor Mapping'

    config_id = fields.Many2one('bill.return.config', required=True, ondelete='cascade')
    location_id = fields.Many2one('stock.location', required=True)
    vendor_id = fields.Many2one('res.partner', required=True, domain="[('supplier_rank', '>', 0)]")
