# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_invoice_order(self, invoice_id):
        related_sols = invoice_id.invoice_line_ids.mapped('sale_line_ids')
        order_id = related_sols[0].order_id if related_sols else False
        return order_id

    @api.multi
    def post(self):

        invoice = self._context.get('invoice', False)

        if invoice:
            if invoice.move_name and invoice.move_name != '/':
                new_name = invoice.move_name
            else:
                # invoice has types:
                # 'out_invoice' -> regular customer invoice
                # 'out_refund' -> customer credit notes
                new_name = ''

                if invoice.type == 'out_invoice' and invoice.origin:
                    order_id = self._get_invoice_order(invoice)
                    if order_id:
                        order_id.write({'number_of_invoices': order_id.number_of_invoices + 1})
                        seq = order_id.number_of_invoices
                        new_name = invoice.origin[2:] + '{0:02d}'.format(seq) if invoice.origin.startswith('SO') \
                            else invoice.origin + '{0:02d}'.format(seq)

                if invoice.type == 'out_refund' and invoice.refund_invoice_id and invoice.refund_invoice_id.number:
                    order_id = self._get_invoice_order(invoice.refund_invoice_id)
                    if order_id:
                        order_id.write({'number_of_credit_notes': order_id.number_of_credit_notes + 1})
                        seq = order_id.number_of_credit_notes
                        new_name = invoice.refund_invoice_id.number[:-2] + 'CM{0:01d}'.format(seq)

                if new_name:
                    # not sure why we need a loop here... just following the convention
                    for move in self:
                        move.name = new_name

        res = super(AccountMove, self).post()

        return res

