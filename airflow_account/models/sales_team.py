# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    phone = fields.Char(string="Phone", default=False, store=True)
    email = fields.Char(string="Email", default=False, store=True)
