# -*- coding: utf-8 -*-
{
    'name': 'Airflow: Account',
    'summary': 'Invoice Sequence to Reference SO Number',
    'description':
    """
What is the business use case for this development?
Air Flow Account
================
* Client is bringing over their orders via API and they have their own SO numbers that they would like to have referenced in the Invoice number to simplify their records. They understand Sale can have more than 1 invoice so they are requesting a sequence to be added after the SO number.
Specification :
Air Flow Account
================
Sales order number example: SO190005AGA01
This comes over as the source document on the Invoice so feel free to code based on Source Doc or on related SO number.
The Invoice number should
    1) remove leading "SO",
    2) Include the full SO number
    3) Add a 2 digit sequence starting with 00 after.
Air Flow Account
================
* Register Payment Discounted Payment Terms

Payment Terms: (We don’t want to affect the normal balance due date.)
    1. Add “Early Discount %” field - integer
    2. Add “Early Payment Days” field – integer

Invoices:
    1. Bring over “Early Discount %” from payment terms
    2. Add field to Calculate “Early Discount Payment Due Date” = Invoice Date + Early Payment Days from payment terms.
    3. Add field to Calculate “Early Discount Amount” = Amount Due x [1-(Early Discount %)]
    4. Add field “Available Discount”,
        4a. If “Early Discount Payment Due Date” <= Today then set “Available Discount” = “Early Discount”
        4b. If “Early Discount Payment Due Date” > Today then set “Available Discount” = 0
        4c. I think we need a scheduled action to compute the available discount daily or have it update when user uses the below action.

Action:
1. Create a new action “Register Discounted Payment” or build off of the existing one. Please display the same action in Customer Invoice Menus + Vendor Bills Menus.
2. Invoice changes :
    2a. Select multiple invoices for same Vendor (required) > action > Register Discounted Payment
    2b. If not same Vendor, produce a blocking error.

Register Payment Screen:
    1. Below usual fields in Register Payment Screen, Display selected Invoices in a list view, with Amount Due (read only), Available Discount (read only), Total to Pay (read only), Total Paid (editable)

        2a. Add a field for Discount Account (many2one = account.account)
        2b. Set default to Purchase Discounts, code = 510200

    3. Sum of Available discount should write off to the Discount Account.
    4. Sum of Total Paid should go to the selected payment account.

5a. If sum of Total Paid = Total to Pay, then entry should be balance and all invoices should be paid.
5b. If sum of Total Paid doesn’t equal Total to Pay, then there should be the option to keep open or write off remaining discrepancy to another account of choice.
     (new) 5b-i. There needs to be a choice of which invoices to remain left open or mark as fully paid.


Specification Custom Check Edits:

Here's the request, I will add to the task:
Adding in the requested Check PDF changes.
1. Replace Odoo Bill Number with Vendor Reference Field.
2. Payment amount column needs to reflect the actual payment being sent, not a calculation.
3a. Remove Balance Due Column, Vendor never needs to see this.
3b. Replace with column for Discount Amount. This should be the discount set at the time of using the new action to register discounted payment.
4. When using action to register discounted payment, make sure invoices not being paid do not show up on the check.
      3a. if you delete a line item this should not show on check details
      3b. if invoice being paid is set to $0 discount, $0 payment, and Leave open, this should not show on check details

Functional Test:
    Test 1. If invoice is for $2,000, but there's a $200 discount, and $1,800 payment, then the discount column should show $200 and the payment amount should show $1,800.
    Test 2. If invoice is for $1,500, but there's a $100 discount, and $1,300 payment with an additional $100 write off, and the invoice is closed, then the discount column should show $100, the payment amount should show $1,300.
    Test 3. If invoice is for $1,500, but there's $100 discount, and $1,200 payment, but the invoice is still open, then the discount column should show $100, and payment should show $1,200.

Air Flow Account Invoice Report Modifications
=============================================
Task ID: 1950508
Custom modifications to the invoice report.

Air Flow Account Customer Statement Modifications
=================================================
Task ID: 2004684
Custom modifications to the CUstomer Statement.


    """,
    'license': 'OEEL-1',
    'author': 'Odoo Inc',
    'version': '0.1.1.1.1',
    'depends': ['sale_management', 'l10n_us_check_printing', 'delivery', 'account_reports', 'account_followup', 'snailmail_account_followup'],
    'data': [

        # security
        # 'security/ir.model.access.csv',

        # # wizard
        # 'wizard/payment_view.xml',
        # # views
        # 'views/account_payment_term_view.xml',
        'views/account_invoice_view.xml',
        'views/sale_order_view.xml',
        'views/report_followup.xml',
        #
        # # reports
        # 'report/print_check.xml',
        'report/account_invoice_report.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
