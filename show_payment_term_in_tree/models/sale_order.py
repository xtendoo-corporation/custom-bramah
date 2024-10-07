import datetime
from collections import OrderedDict

from odoo import api, models, fields
from lxml import html


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment Terms",
        compute='_compute_payment_term_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=True)
