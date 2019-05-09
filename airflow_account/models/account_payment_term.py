# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"
    
    # early_discount = fields.Integer(string='Early Discount(%)')
    early_discount_per = fields.Float(string='Early Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    early_payment_days = fields.Integer(string='Early Payment Days')
