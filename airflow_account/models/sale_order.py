# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    number_of_invoices = fields.Integer('# of Invoices', readonly=True, help='For internal usage only')
    number_of_credit_notes = fields.Integer('# of Credit Notes', readonly=True, help='For internal usage only')

    # The field project_manager is depricated. Airflow wishes to have it hold Char type instead of many2one.
    # Keeping field for historical reasons and data preservation.
    proj_manager = fields.Many2one('res.partner', string="ESTING THIS CHANGEPProject Manager(Depricated)", store=True)

    proj_manager_char = fields.Char(string="Project Manager", store=True)
    proj_name = fields.Char(string="Project Name", store=True)

    ship_date = fields.Date(string="Ship Date", store=True)
    ship_method = fields.Many2one('delivery.carrier', string="Shipping Method", store=True)
