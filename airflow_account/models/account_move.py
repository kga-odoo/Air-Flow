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
        res = super(AccountMove, self).post()
        invoice = self._context.get('invoice', False)

        # invoice has types:
        # 'out_invoice' -> regular customer invoice
        # 'out_refund' -> customer credit notes

        if invoice and invoice.origin:
            new_name = ''

            if invoice.type == 'out_invoice':
                # retrieve the SO to get sequence -> we need to know how many numbered invoices are there already
                order_id = self._get_invoice_order(invoice)

                if order_id:
                    # get last invoice
                    invoices = order_id.invoice_ids.filtered(
                        lambda inv: inv.type == 'out_invoice' and inv.state in ('open', 'paid')
                    )

                    if not invoices:
                        new_name = invoice.origin[2:] + '01' if invoice.origin.startswith('SO') else invoice.origin + '01'
                    else:
                        # based on the last invoice's name
                        try:
                            seq = int(invoices[-1].number[-2:]) + 1
                            new_name = invoice.origin[2:] + '{0:02d}'.format(seq)
                        except ValueError:
                            pass

                    # # our sequence is based on numbered invoices that are not credit notes
                    # sequence = 1 + len(order_id.invoice_ids.filtered(
                    #     lambda inv: inv.type == 'out_invoice' and inv.state in ('open', 'paid'))
                    # )
                    # # this single line of code makes me wanna die
                    # new_name = invoice.origin[2:] + '{0:02d}'.format(sequence) if invoice.origin.startswith('SO') else invoice.origin + '{0:02d}'.format(sequence)

            if invoice.type == 'out_refund':
                if invoice.refund_invoice_id.number:
                    # origin's number + CM + seq
                    # sequence = 1 + len(invoice.refund_invoice_id.refund_invoice_ids.filtered(
                    #     lambda inv: inv.type == 'out_refund' and inv.state in ('open', 'paid'))
                    # )
                    # new_name = invoice.refund_invoice_id.number + 'CM' + str(sequence)

                    # get refund_invoice's order
                    order_id = self._get_invoice_order(invoice.refund_invoice_id)
                    if order_id:
                        # get last invoice
                        invoices = order_id.invoice_ids.filtered(
                            lambda inv: inv.type == 'out_refund' and inv.state in ('open', 'paid')
                        )

                        if not invoices:
                            new_name = invoice.origin[2:] + 'CM1'
                        else:
                            # based on the last invoice's name
                            try:
                                seq = int(invoices[-1].number[-1:]) + 1
                                new_name = invoice.origin[2:] + '{0:01d}'.format(seq)
                            except ValueError:
                                pass

            if new_name:
                # not sure why we need a loop here... just following the convention
                for move in self:
                    move.name = new_name

        return res

