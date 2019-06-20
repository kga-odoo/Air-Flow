# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    early_discount = fields.Integer(related='payment_term_id.early_discount', readonly=True)
    ed_payment_due_date = fields.Date(compute='_compute_early_discount_payment_due_date', string='Early Discount Payment Due Date', store=True)
    early_discount_amount = fields.Float(compute='_compute_early_discount_amount', string='Early Payment Amount', store=True)
    available_discount_hidden = fields.Float(string='Available Discount Force', copy=False)
    do_not_update_discount = fields.Boolean(string='Do not update discount')
    available_discount = fields.Float(compute='_compute_available_discount', inverse='_set_available_discount', string='Available Discount')
    actual_discount = fields.Float(string='Actual Discount', copy=False)  # a discount is used at the Register Payment Discount screen

    sale_id = fields.Many2one('sale.order',compute="_compute_sale_id", string="Original Sale Order",store=True)

    # The field project_manager is depricated. Airflow wishes to have it hold Char type instead of many2one.
    # Keeping field for historical reasons and data preservation.
    proj_manager = fields.Many2one('res.partner', related='sale_id.proj_manager', string="Project Manager(Depricated)", store=True)

    proj_manager_char = fields.Char(related='sale_id.proj_manager_char', string="Project Manager", store=True)
    proj_name = fields.Char(related='sale_id.proj_name', string="Project Name", store=True)

    ship_date = fields.Date(related='sale_id.ship_date', string="Ship Date",store=True)
    ship_method = fields.Many2one('delivery.carrier', related='sale_id.ship_method', string="Shipping Method", store=True)

    @api.multi
    @api.depends('invoice_line_ids','invoice_line_ids.sale_line_ids','invoice_line_ids.sale_line_ids.order_id')
    def _compute_sale_id(self):
        for account in self.filtered(lambda inv: inv.type == 'out_refund' or inv.type == 'out_invoice'):
            # Handle case of credit note
            if account.type == 'out_refund':
                account.sale_id = account.refund_invoice_id.sale_id.id if account.refund_invoice_id.sale_id.id else False
            # Handle case of cust invoice
            elif account.type == 'out_invoice':
                sale_ids = account.mapped('invoice_line_ids.sale_line_ids.order_id')
                account.sale_id = sale_ids[0] if sale_ids else False

    @api.multi
    @api.depends('payment_term_id', 'payment_term_id.early_payment_days', 'date_invoice')
    def _compute_early_discount_payment_due_date(self):
        for invoice in self.filtered(lambda i: i.date_invoice):
            inv_date = fields.Date.from_string(invoice.date_invoice)
            due_date = inv_date + relativedelta(days=invoice.payment_term_id.early_payment_days)
            invoice.ed_payment_due_date = fields.Date.to_string(due_date)

    @api.multi
    @api.depends('payment_term_id', 'payment_term_id.early_discount', 'residual', 'available_discount_hidden', 'do_not_update_discount')
    def _compute_early_discount_amount(self):
        for invoice in self:
            today = fields.Date.context_today(self)
            amount = invoice.residual
            if invoice.do_not_update_discount:
                amount = amount - invoice.available_discount_hidden
            elif invoice.ed_payment_due_date and invoice.ed_payment_due_date >= today:
                amount = amount * (1 - (invoice.early_discount/100))
            invoice.early_discount_amount = amount

    @api.multi
    def _compute_available_discount(self):
        for invoice in self:
            today = fields.Date.context_today(self)
            discount = 0
            if invoice.do_not_update_discount:
                discount = invoice.available_discount_hidden
            elif invoice.ed_payment_due_date and invoice.ed_payment_due_date >= today:
                discount = invoice.residual - invoice.early_discount_amount
            invoice.available_discount = discount

    def _set_available_discount(self):
        for invoice in self:
            invoice.available_discount_hidden = invoice.available_discount

    @api.onchange('do_not_update_discount')
    def onchange_do_not_update_discount(self):
        if self.do_not_update_discount:
            self.available_discount_hidden = self.available_discount
