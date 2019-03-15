# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    early_discount = fields.Integer(string='Early Discount(%)')
    early_payment_days = fields.Integer(string='Early Payment Days')
