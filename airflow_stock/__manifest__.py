# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "AirFlow Stock Customization",
    "summary": "AirFlow Stock Customization",
    "license": "OEEL-1",
    "website": "https://www.odoo.com/page/sale",
    "version": "1.0.1",
    "author": "Odoo Inc",
    "description": """
Air Flow Stock: Transfer and Delivery Slip Modifications
========================================================
Task ID: 1969736

1. Add a new field to transfers called Item Count. = Sum of all Initial Demand Qty. This should be added to Transfers List View. This should also be sortable, planning to prioritized based on larger shipments.

2. Custom Delivery Slip PDF

    1. Help fix logo image sizing for all reports. file attached.

    2a. Add Sales Channel field to the transfer = sale_id.team_id, Add it to the PDF labeled "Sales Rep"
    2b. Pull Sales Channel's phone number to the PDF (no new field needed)
    2c. Pull Sales Channel's email to the PDF (no new field needed)

    3. Add Project Name field to the transfer = sale_id.proj_name, Add it to the PDF

    4. Move the partner_id address on the transfer to the left and label it "Ship To Address"

    5a. If the partner_id on the transfer is a child contact, add the address of the parent contact and keep this labeled "Customer Address"
    5b. If the partner_id on the transfer does not have a parent then repeat the address as the "Customer Address"

    6. Move the origin value next to the name field

    7. Relabel "ORDER (ORIGIN)" into "Air Flow Order #"

    8. Add the SO#

    9. Remove time from datetime

    10. Add Cust Job # field to transfers = sale_id.x_studio_field_osLUc, Add to PDF (moved this field to "job_code" in sale.order)

    11. Add Cust PO # field to transfers = sale_id.client_order_ref, Add to PDF

    12. Add "Shipping Method" field to transfers = sale_id.ship_method, Add to PDF (and hide the default Carrier field)

    13. Rework the Stock Moves with the following fields, add non-existing fields to transfer lines.
        A. relabel "Quantity" to "Qty" on PDF
        B. Model (product_id.x_studio_field_OY1Lv) - add to transfer line + PDF (moved this field to "model" in product.template)
        C. relabel "Product" to Item # on PDF
        D. Product Description (product_id.description_sale) - add to transfer line + PDF
        E. Manufacture (product_id.seller_ids.name) - add to transfer line + PDF
        F. Tag - x_Tag from sale.order.line (moved this field and the referred field to "tag" in sale.order.line and stock.move)

    14. Footer changes in delivery slip:
        A. Replace email to warehouse@airflowreps.com
        B. Remove TIN

    15. Add 3 lines for "Sign", "Date", "Print"

    16. [2071766] Create fields on printed Delivery Order form. Include the following fields:

    16.1 Project Name: to pull from field Project Name (proj_name) on stock.picking record

    16.2 attn: to pull from Ship Attn To (x_studio_field_bekml) on stock.picking record

    16.3 Customer PO: to pull from Customer PO (cust_po) on stock.picking record
     
    17. [2071766] Display Tag information on product list view:

    17.1 Tag information to pull from Studio field x_studio_field_biDgl on stock.pikcing move_line.  

    17.2 Remove Manufacturer column from Delivery slip column

    """,
    "category": "Custom Development",
    "depends": ["airflow_sale", "airflow_account","sale_stock", "delivery", "web"],
    "data": [
        # Views
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
        "views/stock_picking_views.xml",
        # Reports
        "report/report_deliveryslip.xml",
        "report/report_templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
