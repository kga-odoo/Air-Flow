# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']
    sale_order_id = fields.Many2one('sale.order', compute='_compute_origin_sale', string='Sale Order')

    @api.depends('order_line', 'order_line.sale_order_id')
    def _compute_origin_sale(self):
        for purchase in self:
            if purchase.order_line and purchase.order_line[0].sale_order_id:
                sale_ids = purchase.mapped('order_line.sale_order_id')
                purchase.sale_order_id = sale_ids[0] if sale_ids else False
            else:
                purchase.sale_order_id = False

    def action_view_invoice(self, invoices=False):
        result = super(PurchaseOrder, self).action_view_invoice(invoices)
        result['context']['default_orig_purchase_id'] = self.id
        return result
