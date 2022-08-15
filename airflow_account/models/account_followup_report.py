# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class report_account_followup_report(models.AbstractModel):
    _inherit = "account.followup.report"

    def get_pdf(self, options, minimal_layout=True):
        # Pass flag in context so alternate header can be used for this report type
        return super(
            report_account_followup_report, self.with_context(customer_statement=True)
        ).get_pdf(options, minimal_layout=minimal_layout)

    def get_columns_name(self, options):
        headers = super(report_account_followup_report, self).get_columns_name(options)
        if self.env.context.get("print_mode"):
            headers[0] = {"name": _(" Invoice Number "), "style": "white-space:nowrap;"}
            del headers[3]  # Remove "Communications" header
            headers[1:1] = [
                {
                    "name": f" {_('Customer')} PO ",
                    "style": "text-align:center; white-space:nowrap;",
                },
                {
                    "name": f" {_('Reference')} ",
                    "style": "text-align:center; white-space:nowrap;",
                },
            ]
        return headers

    def get_lines(self, options, line_id=None):
        """
        When in print_mode, sort aml lines by due date and add "Reference" column.
        Notes:
        - lines are ordered, and contain some aml lines followed by one/two "total"
          line(s) for each currency.
        - Only reorder aml lines within each currency (i.e one group of aml and total
          lines).
        """
        lines = super(report_account_followup_report, self).get_lines(options, line_id)
        if not self.env.context.get("print_mode"):
            return lines

        # Separate lines by currency (collect aml and total lines separately per group)
        groups = []
        aml_lines = []
        total_lines = []
        _is_line_aml = True
        _is_prev_line_aml = True
        for line in lines:
            # Differentiate between aml and total line based on keys
            _is_line_aml = set(["type", "move_id", "has_invoice"]) <= line.keys()
            # Clear current group if a new group starts. It's a new group if prev line
            # is a total and this line is an aml
            if _is_line_aml and not _is_prev_line_aml:
                if aml_lines or total_lines:
                    groups.append((aml_lines, total_lines))
                aml_lines, total_lines = [], []
            # Collect into appropriate list and update flag
            if _is_line_aml:
                aml_lines.append(line)
            else:
                total_lines.append(line)
            _is_prev_line_aml = _is_line_aml
        # Add trailing lines to group
        if aml_lines or total_lines:
            groups.append((aml_lines, total_lines))

        # Create new processed lines
        new_lines = []
        inv_model = self.env["account.move"]
        aml_model = self.env["account.move.line"]
        for aml_lines, total_lines in groups:
            amls = map(lambda line: line["id"], aml_lines)
            amls = aml_model.browse(amls)
            amls = {aml.id: aml for aml in amls}

            # Sort lines by due date
            # Note: Second column is due date string, but the date format might mess up
            #       sorting, so we get the originl data from the aml
            def _due_date_key(line):
                aml = amls[line["id"]]
                return aml.date_maturity or aml.date

            aml_lines = sorted(aml_lines, key=_due_date_key)

            # Add "Reference" column and move Communication to beginning
            for line in aml_lines:
                aml = amls[line["id"]]
                line["columns"][0:0] = [
                    {"name": line["columns"].pop(2).get("name")},  # Communications
                    {"name": aml.invoice_id.origin},
                ]
                new_lines.append(line)
            # Add empty columns to total lines to line them up
            for line in total_lines:
                line["columns"].insert(0, {"name": False})
                new_lines.append(line)

        return new_lines
