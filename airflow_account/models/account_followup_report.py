# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class report_account_followup_report(models.AbstractModel):
    _inherit = "account.followup.report"

    def get_columns_name(self, options):
        headers = super(report_account_followup_report, self).get_columns_name(options)
        if self.env.context.get("print_mode"):
            headers[0] = {"name": _(" New Invoice # "), "style": "white-space:nowrap;"}
            headers.insert(
                1,
                {
                    "name": _(" Old Reference # "),
                    "style": "text-align:center; white-space:nowrap;",
                },
            )
        return headers

    def get_lines(self, options, line_id=None):
        """
        When in print_mode, sort aml lines by due date and ad "Old Reference #" column.
        Notes:
        - lines are ordered, and contain some aml lines followed by one/two total line(s) for each currency.
        - Only reorder aml lines within each currency (i.e one group of aml and total lines).
        """
        lines = super(report_account_followup_report, self).get_lines(options, line_id)
        if not self.env.context.get("print_mode"):
            return lines

        # Loop through lines and separate lines by currency (collect aml lines and total lines separately per group)
        groups = []
        aml_lines = []
        total_lines = []
        _is_line_aml = True
        _is_prev_line_aml = True
        for line in lines:
            # Differentiate between aml line and total line based on keys
            _is_line_aml = set(["type", "move_id", "has_invoice"]) <= line.keys()
            # Clear current group if it's a new group (prev line is a total, this line is an aml)
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
            print(aml_lines, total_lines)

        # Create new processed lines
        new_lines = []
        inv_model = self.env["account.invoice"]
        aml_model = self.env["account.move.line"]
        for aml_lines, total_lines in groups:
            amls = map(lambda line: line["id"], aml_lines)
            amls = aml_model.browse(amls)
            amls = {aml.id: aml for aml in amls}

            # Sort lines by due date
            # Note: Second column is due date string, but the date format might mess up sorting, so we get the originl data from the aml
            def _due_date_key(line):
                aml = amls[line["id"]]
                return aml.date_maturity or aml.date

            aml_lines = sorted(aml_lines, key=_due_date_key)

            # Add "Old Reference" column
            for line in aml_lines:
                aml = amls[line["id"]]
                src_col = {"name": aml.invoice_id and aml.invoice_id.origin}
                line["columns"].insert(0, src_col)
                new_lines.append(line)
            # Add empty columns to total lines to line them up
            for line in total_lines:
                line["columns"].insert(0, {"name": False})
                new_lines.append(line)

        return new_lines
