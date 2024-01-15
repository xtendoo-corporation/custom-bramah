# Copyright 2023 Camilo Prado
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import base64
import requests
import certifi
import urllib3


import uuid
from ast import literal_eval
from datetime import date, datetime as dt
from io import BytesIO

import xlrd
import xlwt

from odoo import _, fields, api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    from csv import reader
except (ImportError, IOError) as err:
    _logger.error(err)


class BramahStockImport(models.TransientModel):
    _name = "bramah.stock.import"
    _description = "Bramah Stock Import"

    import_file = fields.Binary(string="Import File (*.xlsx)")

    def action_import_file(self):
        """ Process the file chosen in the wizard, create bank statement(s) and go to reconciliation. """
        self.ensure_one()
        if self.import_file:
            self._import_record_data(self.import_file)
        else:
            raise ValidationError(_("Please select Excel file to import"))

    @api.model
    def _import_record_data(self, import_file):
        decoded_data = base64.decodebytes(import_file)
        book = xlrd.open_workbook(file_contents=decoded_data)
        sheet = book.sheet_by_index(0)
        location_id = self.env['stock.location'].search([('name', '=', 'Stock')], limit=1)
        no_procesados = []
        for row in range(1, sheet.nrows):
            default_code = sheet.cell_value(row, 0)
            name = sheet.cell_value(row, 1)
            on_hand = sheet.cell_value(row, 2)
            prevista = sheet.cell_value(row, 3)
            cost = sheet.cell_value(row, 4)
            pvp = sheet.cell_value(row, 5)
            sale_decription = sheet.cell_value(row, 6)
            category_id = sheet.cell_value(row, 7)
            if name:
                product = self.env['product.product'].search([('name', '=', name)])

                if not product:
                    category = self.env['product.category'].search([('name', '=', category_id)], limit=1)
                    product = self.env['product.product'].create({
                        'name': name,
                        'default_code': default_code,
                        'lst_price': pvp,
                        'standard_price': cost,
                        'description_sale': sale_decription,
                        'categ_id': category.id,
                    })
                else:

                    if product and len(product) > 1:
                        product = self.env['product.product'].search(
                            [('name', '=', name), ('default_code', '=', default_code)])
                    if product and len(product) > 1:
                        no_procesados.append(name)
                    else:
                        if product.detailed_type == 'product':
                            self.env['stock.quant'].create({
                                'product_id': product.id,
                                'location_id': location_id.id,
                                'quantity': on_hand,
                            })

        print("*"*80)
        print("No Procesados: ", no_procesados)
        print("*"*80)


