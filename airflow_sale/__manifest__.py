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
    """,
    'category': 'Custom Development',
    'depends': ['sale'],
    'data': [

        # views
        'views/sale_view.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
