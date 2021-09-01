# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError

from odoo.addons import decimal_precision as dp


class AccountRegisterDiscountedPayments(models.TransientModel):
    # """
    #     This wizard is used to pay discounted invoice and partial invoice with option of 'open' and paid invoice
    #     TODO - doesn't work with multi currency
    # """
    _name = 'account.register.discounted.payments'
    _inherit = 'account.payment.register'
    _description = "Register discounted payments on multiple invoices"

    def default_discount_account(self):
        return self.env['account.account'].search([('code', '=', '510200')], limit=1)

    discount_account_id = fields.Many2one('account.account', string='Discount Account',
                                          default=default_discount_account)
    discount_account_label = fields.Char(string='Discount Account Label')
    gain_account_id = fields.Many2one('account.account', string='Gain Account')
    gain_account_label = fields.Char(string='Write-Off Label')
    payment_allocation_ids = fields.One2many('account.discounted.payment.allocation', 'discounted_payment_id',
                                             string='Payment Allocations')
    total_available_discount = fields.Float(compute='_compute_amount', string='Total Available Discount',
                                            digits='Discount')
    total_paid_amount = fields.Float(compute='_compute_amount', string='Total Paid Amount')
    total_to_pay = fields.Float(compute='_compute_amount', string='Total To Pay')
    payment_difference = fields.Float(compute='_compute_amount', string='Payment Difference')
    invoice_ids = fields.Many2many(comodel_name='account.move', relation='account_invoice_payment_discount_trans',
                                   column1='discount_payment_id', column2='discount_invoice_id', string="Invoices",
                                   copy=False, readonly=True)

    @api.depends('payment_allocation_ids')
    def _compute_amount(self):
        for p in self:
            total_available_discount = total_paid_amount = total_to_pay = payment_difference = 0.0
            for allocation in p.payment_allocation_ids:
                total_available_discount += allocation.available_discount
                total_paid_amount += allocation.total_paid
                total_to_pay += allocation.total_to_pay
                if allocation.status == 'paid':
                    payment_difference += allocation.total_to_pay - allocation.total_paid

            p.total_available_discount = total_available_discount
            p.total_paid_amount = total_paid_amount
            p.total_to_pay = total_to_pay
            p.payment_difference = payment_difference

    @api.model
    def default_get(self, fields):
        rec = super(AccountRegisterDiscountedPayments, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        if rec.get('multi'):
            raise UserError(_("You can only register payments for same partner"))
        if active_ids:
            invoices = self.env['account.move'].browse(active_ids)
            rec['payment_allocation_ids'] = [(0, 0, {
                'invoice_id': i.id,
                'residual': i.amount_residual,
                'available_discount': i.available_discount,
                'total_paid': i.amount_residual - i.available_discount,
                'status': 'paid',
                # MIG, v13 reference field removed
                # 'reference': i.reference,
                'total_to_pay': i.amount_residual - i.available_discount}) for i in invoices]
        return rec

    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterDiscountedPayments, self)._prepare_payment_vals(invoices)
        res.update(
            amount=self.total_paid_amount,
            total_available_discount=self.total_available_discount,
            total_to_pay=self.total_to_pay,
            discount_account_id=self.discount_account_id.id,
            gain_account_id=self.gain_account_id.id,
            discount_account_label=self.discount_account_label or _('Discount'),
            gain_account_label=self.gain_account_label or _('Write-Off'),
            payment_allocation_ids=[(0, 0, {
                'invoice_id': i.invoice_id.id,
                'residual': i.amount_residual,
                'available_discount': i.available_discount,
                'total_paid': i.total_paid,
                'status': i.status,
                'total_to_pay': i.total_to_pay}) for i in self.payment_allocation_ids if
                                    i.available_discount > 0 or i.total_paid > 0])
        return res

    def create_payments(self):
        if not self.payment_allocation_ids:
            raise UserError(_('You should have atleast one invoice selected'))
        if self.total_available_discount == 0 and self.total_paid_amount == 0 and self.payment_difference == 0:
            raise UserError(_('You can not paid zero amount'))
        res = super(AccountRegisterDiscountedPayments, self).create_payments()
        for allocation in self.mapped('payment_allocation_ids'):
            allocation.invoice_id.actual_discount += allocation.available_discount
        return res


class AccountDiscountedPaymentsAllocation(models.TransientModel):
    _name = 'account.discounted.payment.allocation'
    _inherit = 'account.payment.allocation'
    _description = "Register discounted payments allocation"

    discounted_payment_id = fields.Many2one('account.register.discounted.payments', string='Discounted Payment')
    reference = fields.Char()

    @api.onchange('available_discount')
    def onchange_available_discount(self):
        self.total_to_pay = self.residual - self.available_discount
        self.total_paid = self.total_to_pay
