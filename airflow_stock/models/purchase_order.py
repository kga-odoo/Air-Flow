# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # x_Attention
    # ship_attn = fields.Char(string='Attention', copy=True)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    # x_Tag
    tag = fields.Char('Tag')
