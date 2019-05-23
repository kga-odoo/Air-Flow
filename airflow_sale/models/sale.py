# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    job_code = fields.Char(string="Job Code")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    tag = fields.Char(string='Tag')

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['account_analytic_id'] = self.analytic_account_id.id or self.order_id.analytic_account_id.id
        return res
