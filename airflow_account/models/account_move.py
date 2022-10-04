# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_invoice_order(self, invoice_id):
        related_sols = invoice_id.invoice_line_ids.mapped('sale_line_ids')
        order_id = related_sols[0].order_id if related_sols else False
        return order_id

    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        super()._compute_name()
        self._update_name_from_origin()

    def _update_name_from_origin(self):
        for invoice in self:
            if invoice.move_type == 'out_invoice' and invoice.invoice_origin:
                order_id = self._get_invoice_order(invoice)
                if order_id:
                    order_id.write({'number_of_invoices': order_id.number_of_invoices + 1})
                    seq = order_id.number_of_invoices
                    invoice.name = invoice.invoice_origin[2:] + '{0:02d}'.format(
                        seq) if invoice.invoice_origin.startswith('SO') \
                        else invoice.invoice_origin + '{0:02d}'.format(seq)

            if invoice.move_type == 'out_refund' and invoice.reversed_entry_id and invoice.reversed_entry_id.name:
                order_id = self._get_invoice_order(invoice.reversed_entry_id)
                if order_id:
                    order_id.write({'number_of_credit_notes': order_id.number_of_credit_notes + 1})
                    seq = order_id.number_of_credit_notes
                    invoice.name = invoice.reversed_entry_id.name[:-2] + 'CM{0:01d}'.format(seq)
