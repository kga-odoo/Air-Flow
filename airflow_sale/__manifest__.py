# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'AirFlow Sale Customization',
    'summary': 'AirFlow Sale Customization',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com/page/sale',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
Air Flow Sale
================
* Analytic account at So line level instead of SO

Air Flow Sale: Vendor Bill link to SO
======================================
This company has many dropships. Vendor Bill and Purchase Orders needs to display a direct link to Sales Order. Researching Source Number takes too much time.


    """,
    'category': 'Custom Development',
    'depends': ['sale', 'purchase', 'stock_dropshipping'],
    'data': [

        # views
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/vendor_bill_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
