# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    number_of_invoices = fields.Integer('# of Invoices', readonly=True, help='For internal usage only')
    number_of_credit_notes = fields.Integer('# of Credit Notes', readonly=True, help='For internal usage only')

    proj_manager = fields.Many2one('res.partner', string="Project Manager", default=False, store=True)
    proj_name = fields.Char(string="Project Name", default=False, store=True)

    ship_date = fields.Date(string="Ship Date", default=False, store=True)
    ship_method = fields.Many2one('delivery.carrier', string="Shipping Method", default=False, store=True)
