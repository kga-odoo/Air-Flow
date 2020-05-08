# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    orig_purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    sale_order_id = fields.Many2one(related='orig_purchase_id.sale_order_id', string='Sale Order')

    # @api.multi
    # @api.depends('invoice_line_ids', 'invoice_line_ids.purchase_id')
    # def _compute_origin_sale(self):
    #     for bill in self.filtered(lambda b: b.invoice_line_ids and b.invoice_line_ids[0].purchase_id):
    #         purchase_ids = bill.mapped('invoice_line_ids.purchase_id')
    #         bill.orig_purchase_id = purchase_ids[0] if purchase_ids else False

    @api.model
    def create(self, vals):
        vals.update({'orig_purchase_id': self._context.get('default_purchase_id')})
        res = super(AccountInvoice, self).create(vals)
        print("test on create")
        return res
