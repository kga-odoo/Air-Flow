# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta
from odoo import api, models, fields
from odoo.addons import decimal_precision as dp
import logging


_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    paid_date = fields.Date(string='Paid Date')
    sale_id = fields.Many2one('sale.order',compute="_compute_sale_id", string="Original Sale Order",store=True)

    # The field project_manager is depricated. Airflow wishes to have it hold Char type instead of many2one.
    # Keeping field for historical reasons and data preservation.
    proj_manager = fields.Many2one('res.partner', related='sale_id.proj_manager', string="Project Manager(Depricated)", store=True)

    proj_manager_name = fields.Char(related='sale_id.proj_manager_name', string="Project Manager", store=True)
    proj_name = fields.Char(related='sale_id.proj_name', string="Project Name", store=True)

    ship_date = fields.Date(related='sale_id.ship_date', string="Ship Date",store=True)
    ship_method = fields.Many2one('delivery.carrier', related='sale_id.ship_method', string="Shipping Method", store=True)

    @api.depends('invoice_line_ids','invoice_line_ids.sale_line_ids','invoice_line_ids.sale_line_ids.order_id')
    def _compute_sale_id(self):
        for account in self:
            # Handle case of credit note
            # [MIG] now handled in reversal wizard
            # if account.type == 'out_refund':
            #     account.sale_id = account.refund_invoice_id.sale_id.id if account.refund_invoice_id.sale_id.id else False
            # Handle case of cust invoice
            if account.type == 'out_invoice':
                sale_ids = account.mapped('invoice_line_ids.sale_line_ids.order_id')
                account.sale_id = sale_ids[0] if sale_ids else False
            else:
                account.sale_id = False

    def write(self, vals):
        """Inherit to set the paid date"""
        if vals.get('state') == 'paid':
            vals['paid_date'] = fields.Date.context_today(self)
        return super(AccountMove, self).write(vals)
