# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, format_date
LINE_FILLER = '*'
INV_LINES_PER_STUB = 9

class AccountPayment(models.Model):
    _inherit = "account.payment"

    total_available_discount = fields.Float(string='Total Available Discount')
    total_paid_amount = fields.Float(string='Total Paid Amount')
    total_to_pay = fields.Float(string='Total To Pay')
    discount_account_id = fields.Many2one('account.account', string='Discount Account',)
    gain_account_id = fields.Many2one('account.account', string='Gain Account')
    payment_allocation_ids = fields.One2many('account.payment.allocation', 'payment_id', string='Payment Allocations')
    discount_account_label = fields.Char(string='Discount Account Label')
    gain_account_label = fields.Char(string='Write-Off Label')

    def _calculate_partial_payment(self, move, amount, invoice, invoice_currency):
        """ Create a journal entry corresponding to partial payment and manage currency difference of amount"""
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
        partial_counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        partial_counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        partial_counterpart_aml_dict.update({'currency_id': currency_id, 'name': invoice.number if invoice else False})
        counterpart_aml = aml_obj.create(partial_counterpart_aml_dict)
        return counterpart_aml

    def _create_write_off_line(self, amount, move, account_id, label, invoice_currency):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
        amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
        amount_wo = amount * (self.payment_type == 'outbound' and -1 or 1)

        if amount_wo > 0:
            debit_wo = amount_wo
            credit_wo = 0.0
            amount_currency_wo = abs(amount_currency_wo)
        else:
            debit_wo = 0.0
            credit_wo = -amount_wo
            amount_currency_wo = -abs(amount_currency_wo)

        writeoff_line['name'] = label
        writeoff_line['account_id'] = account_id.id
        writeoff_line['debit'] = debit_wo
        writeoff_line['credit'] = credit_wo
        writeoff_line['amount_currency'] = amount_currency_wo
        writeoff_line['currency_id'] = currency_id
        aml_obj.create(writeoff_line)

    def _create_payment_entry(self, amount):
        """
            Override to add the logic of partial payment and discounted payment, changes are marked with custom code
        """
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            #if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        if not self.payment_allocation_ids or self.payment_type == 'transfer':
            counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
            counterpart_aml_dict.update({'currency_id': currency_id})
            counterpart_aml = aml_obj.create(counterpart_aml_dict)
        else:
            # CUSTOM CODE START

            allocated_amount = amount_to_left = 0.0
            # calculate partial paid invoicies
            for allocation in self.payment_allocation_ids:
                if allocation.status == 'paid':
                    amount_to_left += allocation.total_to_pay - allocation.total_paid
                    allocated_amount = allocation.total_to_pay + allocation.available_discount
                else:
                    allocated_amount = allocation.total_paid + allocation.available_discount
                allocated_amount = allocated_amount * (self.payment_type == 'outbound' and 1 or -1)
                counterpart_aml = self._calculate_partial_payment(move, allocated_amount, allocation.invoice_id, invoice_currency)
                # reconsile with invoice
                allocation.invoice_id.register_payment(counterpart_aml)
            if self.discount_account_id and self.total_available_discount:
                self._create_write_off_line(self.total_available_discount, move, self.discount_account_id, self.discount_account_label, invoice_currency)
            if amount_to_left:
                self._create_write_off_line(amount_to_left, move, self.gain_account_id, self.gain_account_label, invoice_currency)
        # CUSTOM CODE END

        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency
            # minus the payment amount in company currency, and not from the payment difference in the payment currency
            # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
            # amout_wo must be positive for out_invoice and in_refund and negative for in_invoice and out_refund in standard use case
            #               |   total_payment_company_signed   |    total_residual_company_signed    |    amount_wo
            #----------------------------------------------------------------------------------------------------------------------
            # in_invoice    |   positive                       |    positive                         |    negative
            #----------------------------------------------------------------------------------------------------------------------
            # in_refund     |   positive                       |    negative                         |    positive
            #----------------------------------------------------------------------------------------------------------------------
            # out_invoice   |   positive                       |    positive                         |    positive
            #----------------------------------------------------------------------------------------------------------------------
            # out_refund    |   positive                       |    negative                         |    negative
            #----------------------------------------------------------------------------------------------------------------------
            # DO NOT FORWARD-PORT
            if self.invoice_ids[0].type == 'in_invoice':
                amount_wo = total_payment_company_signed - total_residual_company_signed
            elif self.invoice_ids[0].type == 'in_refund':
                amount_wo = - total_payment_company_signed - total_residual_company_signed
            elif self.invoice_ids[0].type == 'out_refund':
                amount_wo = total_payment_company_signed + total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
            # amount in the company currency
            if amount_wo > 0:
                debit_wo = amount_wo
                credit_wo = 0.0
                amount_currency_wo = abs(amount_currency_wo)
            else:
                debit_wo = 0.0
                credit_wo = -amount_wo
                amount_currency_wo = -abs(amount_currency_wo)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        move.post()

        #reconcile the invoice receivable/payable line(s) with the payment

        # Custom Code
        if not self.payment_allocation_ids:
            self.invoice_ids.register_payment(counterpart_aml)

        return move

    # this is also entirely overloaded.
    # can we stop this kind of dev in the future? It is utterly terrible. Mark my word. -- EHE
    def make_stub_line(self, invoice):
        """ Return the dict used to display an invoice/refund in the stub
        """
        # Find the account.partial.reconcile which are common to the invoice and the payment
        if invoice.type in ['in_invoice', 'out_refund']:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_debit_ids').filtered(lambda r: r.debit_move_id in self.move_line_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_credit_ids').filtered(lambda r: r.credit_move_id in self.move_line_ids)

        if self.currency_id != self.journal_id.company_id.currency_id:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount')))

        amount_residual = invoice_sign * invoice.residual
        original_res =  {
            'due_date': format_date(self.env, invoice.date_due),
            'number': invoice.reference and invoice.number + ' - ' + invoice.reference or invoice.number,
            'amount_total': formatLang(self.env, invoice_sign * invoice.amount_total, currency_obj=invoice.currency_id),
            'amount_residual': formatLang(self.env, amount_residual, currency_obj=invoice.currency_id) if amount_residual*10**4 != 0 else '-',
            'amount_paid': formatLang(self.env, invoice_sign * amount_paid, currency_obj=invoice.currency_id),
            'currency': invoice.currency_id,
        }

        # previous custom code here
        allocations = self.payment_allocation_ids.filtered(lambda a: a.invoice_id.id == invoice.id)
        total_paid = allocations and allocations[0].total_paid or 0
        original_res.update(
            number=invoice.reference or invoice.number,
            discount=formatLang(self.env, invoice_sign * invoice.actual_discount, currency_obj=invoice.currency_id),
            payment_amount=formatLang(self.env, invoice_sign * total_paid, currency_obj=invoice.currency_id),
            skip=invoice.actual_discount == 0 and total_paid == 0 or False
        )
        res = [original_res]
        for payment in invoice.payment_ids:
            print(payment, payment.name, payment.amount)
            payment_info = original_res.copy()
            payment_info.update(payment_amount=formatLang(self.env, invoice_sign * payment.amount, currency_obj=invoice.currency_id))
            res.append(payment_info)
        
        return res

    def get_pages(self):
        pages = super(AccountPayment, self).get_pages()
        for page in pages:
            is_discounted_payment = self.payment_allocation_ids and True or False
            page['is_discounted_payment'] = is_discounted_payment,
            page['partner_type'] = self.partner_type
            if is_discounted_payment:
                for line in page['stub_lines']:
                    if line['skip']:
                        page['stub_lines'].remove(line)
        return pages

    def make_stub_lines(self, invoices):
        res = []
        for invoice in invoices:
            res.extend(self.make_stub_line(invoice))
        return res

    # need to overload this method here to force multiple stub_lines
    def make_stub_pages(self):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        if len(self.invoice_ids) == 0:
            return None

        multi_stub = self.company_id.us_check_multi_stub

        invoices = self.invoice_ids.sorted(key=lambda r: r.date_due)
        debits = invoices.filtered(lambda r: r.type == 'in_invoice')
        credits = invoices.filtered(lambda r: r.type == 'in_refund')

        # customization code starts
        # Prepare the stub lines
        if not credits:
            stub_lines = self.make_stub_lines(invoices) # [self.make_stub_line(inv) for inv in invoices]
        else:
            stub_lines = [{'header': True, 'name': "Bills"}]
            stub_lines += self.make_stub_lines(debits)
            stub_lines += [{'header': True, 'name': "Refunds"}]
            stub_lines += self.make_stub_lines(credits)
        # customization code ends

        # Crop the stub lines or split them on multiple pages
        if not multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                # Make sure we don't start the credit section at the end of a page
                if len(stub_lines) >= i+INV_LINES_PER_STUB and stub_lines[i+INV_LINES_PER_STUB-1].get('header'):
                    num_stub_lines = INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
                else:
                    num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i+num_stub_lines])
                i += num_stub_lines

        return stub_pages

class AccountDiscountedPaymentsAllocation(models.Model):
    _name = 'account.payment.allocation'

    payment_id = fields.Many2one('account.payment', string='Payment')
    invoice_id = fields.Many2one('account.invoice', string='Invoice', required=True)
    residual = fields.Float(string='Amount Due')
    available_discount = fields.Float(string='Available Discount')
    total_to_pay = fields.Float(string='Total To Pay')
    total_paid = fields.Float(string='Total Paid', required=True)
    status = fields.Selection([('open', 'Open'), ('paid', 'Paid')], string='Invoice Status', required=True)

    @api.multi
    @api.constrains('total_to_pay', 'total_paid')
    def _check_paid_amount(self):
        for allocation in self:
            if allocation.total_paid > allocation.total_to_pay:
                raise UserError(_("You can not pay more than amount to pay."))
