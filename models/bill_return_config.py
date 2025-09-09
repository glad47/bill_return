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

    # intermediate_location_id = fields.Many2many(
    #     'stock.location',
    #     'bill_return_config_intermediate_location_rel',
    #     'config_id',
    #     'location_id',
    #     string="Intermediate Transit",
    #     help="Transit or staging location used during the operation"
    # )

    # default_intermediate_location_id = fields.Many2one(
    #     'stock.location',
    #     string="Default Intermediate Location",
    #     domain="[('id', 'in', intermediate_location_id)]",
    #     help="Primary transit location used by default"
    # )

    # vendor_ids = fields.Many2many(
    #     'res.partner',
    #     string="Contact Address",
    #     domain="[('supplier_rank', '>', 0)]",
    #     help="Vendors participating in this operation"
    # )

    # picking_type_ids = fields.Many2many(
    #     'stock.picking.type',
    #     string="Picking Types",
    #     help="Relevant picking types for this operation"
    # )

    location_vendor_map_ids = fields.One2many(
        'bill.return.location.vendor',
        'config_id',
        string="Location-Vendor Mapping"
    )


    location_picking_type_map_ids = fields.One2many(
        'bill.return.location.picking.type',
        'config_id',
        string="Location-Picking Type Mapping",
        help="Explicit mapping between each location and its internal picking type"
    )



    @api.constrains('default_location_id', 'location_ids')
    def _check_default_location(self):
        for rec in self:
            if rec.default_location_id and rec.default_location_id not in rec.location_ids:
                raise ValidationError("Default storage location must be one of the selected storages.")

   


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
    


    @api.constrains('location_ids', 'location_vendor_map_ids')
    def _check_location_vendor_mapping_required(self):
        for rec in self:
            if rec.location_ids:
                mapped_locations = rec.location_vendor_map_ids.mapped('location_id')
                missing_locations = rec.location_ids - mapped_locations
                if missing_locations:
                    names = ', '.join(missing_locations.mapped('complete_name'))
                    raise ValidationError(
                        f"Each selected location must have a vendor mapping. Missing: {names}"
                    )
                


    @api.constrains('location_ids', 'location_picking_type_map_ids')
    def _check_location_picking_type_mapping(self):
        for rec in self:
            if rec.location_ids:
                mapped_locations = rec.location_picking_type_map_ids.mapped('location_id')
                missing = rec.location_ids - mapped_locations
                if missing:
                    names = ', '.join(missing.mapped('complete_name'))
                    raise ValidationError(f"Missing picking type mapping for locations: {names}")
            




    

    def _get_action_bulk_bill_return(self):
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

