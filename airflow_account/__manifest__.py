# -*- coding: utf-8 -*-
{
    'name': 'airflow: sale',
    'summary': 'Invoice Sequence to Reference SO Number',
    'description':
    """
    What is the business use case for this development?
    Client is bringing over their orders via API and they have their own SO numbers that they would like to have referenced in the Invoice number to simplify their records. They understand Sale can have more than 1 invoice so they are requesting a sequence to be added after the SO number. 
    Specification :
    Sales order number example: SO190005AGA01
    This comes over as the source document on the Invoice so feel free to code based on Source Doc or on related SO number.
    The Invoice number should
    (1) remove leading "SO", 
    (2) Include the full SO number 
    (4) Add a 2 digit sequence starting with 00 after.
    See below for acceptance testing
    """,
    'license': 'OEEL-1',
    'author': 'Odoo Inc',
    'version': '0.1',
    'depends': ['sale_management', 'account'],
    'data': [
    ],
}