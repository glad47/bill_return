
from odoo import models, fields, api
from odoo.exceptions import ValidationError



class BillReturnLocationPickingType(models.Model):
    _name = 'bill.return.location.picking.type'
    _description = 'Location-Picking Type Mapping'

    config_id = fields.Many2one('bill.return.config', required=True, ondelete='cascade')
    location_id = fields.Many2one('stock.location', required=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        required=True,
        domain="[('code', '=', 'internal')]",
        string="Internal Picking Type"
    )
