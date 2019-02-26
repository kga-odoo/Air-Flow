# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    number_of_invoices = fields.Integer('# of Invoices', readonly=True, help='For internal usage only')
    number_of_credit_notes = fields.Integer('# of Credit Notes', readonly=True, help='For internal usage only')

