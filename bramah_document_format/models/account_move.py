import datetime
from collections import OrderedDict

from odoo import api, models
from odoo.tools import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_sale_order_note(self,sale_order_id):
        sale_order = self.env['sale.order'].search([('id', '=', sale_order_id)])
        print("*"*50)
        print("ENTRA")
        print("note", sale_order.note)
        print("*"*50)
        return sale_order.note
