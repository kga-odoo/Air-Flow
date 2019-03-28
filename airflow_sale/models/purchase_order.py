# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields

class PurchaseOrder(models.Model):
    _inherit = [
     'purchase.order']
    sale_order_id = fields.Many2one('sale.order', compute='_compute_origin_sale', string='Sale Order')

    @api.multi
    @api.depends('order_line', 'order_line.sale_line_id', 'order_line.sale_line_id.order_id')
    def _compute_origin_sale(self):
        for purchase in self.filtered(lambda p: p.order_line and p.order_line[0].sale_line_id):
            purchase.sale_order_id = purchase.order_line[0].sale_line_id.order_id
            print(purchase.sale_order_id)
