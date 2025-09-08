from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BillReturnConfig(models.Model):
    _name = 'bill.return.config'
    _description = 'Bulk Bill Return Operation Configuration'
    _rec_name = 'name'

    name = fields.Char(
        string="Configuration Name",
        required=True,
        default="Bulk Bill Return Configuration"
    )

    location_ids = fields.Many2many(
        'stock.location',
        'bill_return_config_location_rel',
        'config_id',
        'location_id',
        string="Storages",
        help="All locations involved in this operation"
    )

    default_location_id = fields.Many2one(
        'stock.location',
        string="Default Storage Location",
        domain="[('id', 'in', location_ids)]",
        help="Primary location used by default for bill returns"
    )

    intermediate_location_id = fields.Many2many(
        'stock.location',
        'bill_return_config_intermediate_location_rel',
        'config_id',
        'location_id',
        string="Intermediate Transit",
        help="Transit or staging location used during the operation"
    )

    default_intermediate_location_id = fields.Many2one(
        'stock.location',
        string="Default Intermediate Location",
        domain="[('id', 'in', intermediate_location_id)]",
        help="Primary transit location used by default"
    )

    vendor_ids = fields.Many2many(
        'res.partner',
        string="Contact Address",
        domain="[('supplier_rank', '>', 0)]",
        help="Vendors participating in this operation"
    )

    picking_type_ids = fields.Many2many(
        'stock.picking.type',
        string="Picking Types",
        help="Relevant picking types for this operation"
    )

    @api.constrains('default_location_id', 'location_ids')
    def _check_default_location(self):
        for rec in self:
            if rec.default_location_id and rec.default_location_id not in rec.location_ids:
                raise ValidationError("Default storage location must be one of the selected storages.")

    @api.constrains('default_intermediate_location_id', 'intermediate_location_id')
    def _check_default_intermediate_location(self):
        for rec in self:
            if rec.default_intermediate_location_id and rec.default_intermediate_location_id not in rec.intermediate_location_id:
                raise ValidationError("Default intermediate location must be one of the selected transit locations.")


    @api.model
    def create(self, vals):
        if self.search_count([]) > 0:
            raise ValidationError("Only one Bill Return Configuration is allowed.")
        return super().create(vals)

    def write(self, vals):
        if len(self) > 1:
            raise ValidationError("You cannot modify multiple Bill Return Configurations at once.")
        return super().write(vals)
    

    @api.model
    def get_singleton_record(self):
        return self.search([], limit=1)
    

    def _get_action_bulk_bill_return(self):
        print("*****************************************************")
        record = self.env['bill.return.config'].search([], limit=1)
        print(record)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bulk Bill Return',
            'res_model': 'bill.return.config',
            'view_mode': 'form',
            'res_id': record.id,
            'target': 'current',
        }

