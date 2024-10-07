import datetime
from collections import OrderedDict

from odoo import api, models, fields
from lxml import html


class AccountMove(models.Model):
    _inherit = "account.move"


    invoice_payment_term_id = fields.Many2one(
            comodel_name='account.payment.term',
            string='Payment Terms',
            compute='_compute_invoice_payment_term_id', store=True, readonly=False, precompute=True,
            states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]},
            check_company=True,
            tracking=True
        )
