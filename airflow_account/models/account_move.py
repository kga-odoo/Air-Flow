from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    paid_date = fields.Date(string='Paid Date')
    sale_id = fields.Many2one('sale.order', compute="_compute_sale_id", string="Original Sale Order", store=True)

    # The field project_manager is depricated. Airflow wishes to have it hold Char type instead of many2one.
    # Keeping field for historical reasons and data preservation.
    proj_manager = fields.Many2one('res.partner', related='sale_id.proj_manager', string="Project Manager(Depricated)",
                                   store=True)

    proj_manager_name = fields.Char(related='sale_id.proj_manager_name', string="Project Manager", store=True)
    proj_name = fields.Char(related='sale_id.proj_name', string="Project Name", store=True)

    ship_date = fields.Date(related='sale_id.ship_date', string="Ship Date", store=True)
    ship_method = fields.Many2one('delivery.carrier', related='sale_id.ship_method', string="Shipping Method",
                                  store=True)

    @api.depends('invoice_line_ids', 'invoice_line_ids.sale_line_ids', 'invoice_line_ids.sale_line_ids.order_id')
    def _compute_sale_id(self):
        for account in self:
            # Handle case of credit note
            # [MIG] now handled in reversal wizard
            # if account.type == 'out_refund':
            #     account.sale_id = account.refund_invoice_id.sale_id.id if account.refund_invoice_id.sale_id.id else False
            # Handle case of cust invoice
            if account.move_type == 'out_invoice':
                sale_ids = account.mapped('invoice_line_ids.sale_line_ids.order_id')
                account.sale_id = sale_ids[0] if sale_ids else False
            else:
                account.sale_id = False

    def write(self, vals):
        """Inherit to set the paid date"""
        if vals.get('state') == 'paid':
            vals['paid_date'] = fields.Date.context_today(self)
        return super(AccountMove, self).write(vals)

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
