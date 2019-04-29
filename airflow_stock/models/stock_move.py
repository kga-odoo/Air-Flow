# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_model = fields.Char(string="Model", related="product_id.model")
    product_description = fields.Text(
        string="Product Description", related="product_id.description_sale"
    )
    manufacturer = fields.Many2one(
        string="Manufacturer", related="product_id.seller_ids.name"
    )
