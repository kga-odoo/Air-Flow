# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # x_Attention 
    ship_attn = fields.Char(string='Attention', copy=True)
