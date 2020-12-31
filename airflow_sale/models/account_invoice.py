# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = ['account.move']

    orig_purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    sale_order_id = fields.Many2one(related='orig_purchase_id.sale_order_id', string='Sale Order')

    # @api.depends('invoice_line_ids', 'invoice_line_ids.purchase_line_id', 'invoice_line_ids.purchase_line_id.order_id')
    # def _compute_origin_sale(self):
    #     for bill in self.filtered(lambda b: b.invoice_line_ids.purchase_line_id and b.invoice_line_ids[0].purchase_line_id.order_id):
    #         purchase_ids = bill.mapped('invoice_line_ids.purchase_line_id.order_id')
    #         bill.orig_purchase_id = purchase_ids[0] if purchase_ids else False
