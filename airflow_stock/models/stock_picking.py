# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockPicking(models.Model):
    _inherit = "stock.picking"

    item_count = fields.Float(
        sting="Item Count",
        compute="_compute_item_count",
        digits="Product Unit of Measure",
        store=True,
    )
    sales_rep = fields.Many2one(string="Sales Rep", related="sale_id.team_id")
    ship_method = fields.Many2one(
        sting="Shipping Method", related="sale_id.ship_method"
    )
    proj_name = fields.Char(string="Project Name", related="sale_id.proj_name")
    job_code = fields.Char(string="Job Code", related="sale_id.job_code")
    cust_po = fields.Char(string="Customer PO", related="sale_id.client_order_ref")
    
    # x_studio_field_bekml
    ship_attn = fields.Char(string='Ship Attn To', related='sale_id.ship_attn')

    @api.depends("move_lines.product_uom_qty")
    def _compute_item_count(self):
        for picking in self:
            picking.item_count = sum(picking.move_lines.mapped("product_uom_qty"))
