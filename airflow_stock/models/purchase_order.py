# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    tag = fields.Char('Tag')
