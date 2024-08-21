import datetime
from collections import OrderedDict

from odoo import api, models
from lxml import html


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_sale_order_note(self,sale_order_id):
        sale_order = self.env['sale.order'].search([('id', '=', sale_order_id)], limit=1)
        if sale_order and sale_order.note:
            note_text = html.fromstring(sale_order.note).text_content().strip()
            if note_text:
                return sale_order.note
        return None
