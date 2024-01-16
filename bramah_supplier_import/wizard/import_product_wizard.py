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


class BramahSupplierImport(models.TransientModel):
    _name = "bramah.supplier.import"
    _description = "Bramah Suplier Import"

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
        # try:
        decoded_data = base64.decodebytes(import_file)
        book = xlrd.open_workbook(file_contents=decoded_data)
        sheet = book.sheet_by_index(0)
        name = ''
        ref = ''
        no_procesado = []
        print("*" * 80)
        for row in range(1, sheet.nrows):
            if sheet.cell_value(row, 0):
                name = sheet.cell_value(row, 0)
            if sheet.cell_value(row, 1):
                ref = sheet.cell_value(row, 1)
            if name:
                product_template = self._search_product_template(name, ref)
                if product_template and len(product_template) > 1:
                    no_procesado.append(name)
                else:
                    if product_template:
                        supplier_id = self._search_suplier(sheet.cell_value(row, 2))
                        if supplier_id:
                            self.env["product.supplierinfo"].create(
                                {
                                    "partner_id": supplier_id.id,
                                    "product_tmpl_id": product_template.id,
                                    "product_code": sheet.cell_value(row, 5),
                                    "price": sheet.cell_value(row, 4),
                                }
                            )
        print("no_procesado:", no_procesado)
        print("*" * 80)
        # except xlrd.XLRDError:
        #     raise ValidationError(
        #         _("Invalid file style, only .xls or .xlsx file allowed")
        #     )
        # except Exception as e:
        #     raise e

    def _search_product_template(self, name, ref):
        if not name:
            return

        product_template = self.env["product.template"].search(
            [("name", "=", name), ("default_code", "=", ref)]
        )
        if product_template:
            return product_template
        else:
            return

    def _search_suplier(self, supplier_name):
        if not supplier_name:
            return
        res_partner = self.env["res.partner"].search(
            [("name", "=", supplier_name)],
            limit=1
        )
        if res_partner:
            return res_partner

    # def _search_or_create_category(self, category):
    #     if not category:
    #         return
    #     result = self.env["product.category"].search([("name", "=", category.strip())])
    #     if result:
    #         return result
    #     return self.env["product.category"].create(
    #         {
    #             "name": category,
    #             "parent_id": self.env.ref('product.product_category_all').id,
    #         }
    #     )
    #
    # def _search_or_create_product_tag(self, product_tag):
    #     if not product_tag:
    #         return
    #     result = self.env["product.tag"].search([("name", "=", product_tag.strip())])
    #     if result:
    #         return result
    #     return self.env["product.tag"].create({"name": product_tag})
    #
    # def _search_or_create_public_categ(self, category_web, category_ecommerce):
    #     if not category_web:
    #         return
    #     result_web = self.env["product.public.category"].search([("name", "=", category_web.strip())])
    #     if not result_web:
    #         result_web = self.env["product.public.category"].create({"name": category_web})
    #     if not category_ecommerce:
    #         return result_web
    #
    #     result_ecommerce = self.env["product.public.category"].search(
    #         [
    #             ("name", "=", category_ecommerce),
    #             ("parent_id", "=", result_web.id),
    #         ]
    #     )
    #     if not result_ecommerce:
    #         result_ecommerce = self.env["product.public.category"].create(
    #             {
    #                 "name": category_ecommerce,
    #                 "parent_id": result_web.id,
    #             }
    #         )
    #     return result_ecommerce
    #
    # def _search_or_create_product_attribute(self, product_attribute):
    #     result = self.env["product.attribute"].search([("name", "=", product_attribute.strip())])
    #     if result:
    #         return result
    #     result = self.env["product.attribute"].create(
    #         {"name": product_attribute}
    #     )
    #     return result
    #
    # def _search_or_create_product_attribute_value(self, product_attribute_color, product_attribute_value):
    #     product_attribute_color_id = product_attribute_color[0].id
    #     result = self.env["product.attribute.value"].search(
    #         [
    #             ("attribute_id", "=", product_attribute_color_id),
    #             ("name", "=", product_attribute_value),
    #         ]
    #     )
    #     if result:
    #         return result
    #     return self.env["product.attribute.value"].create(
    #         {
    #             "attribute_id": product_attribute_color_id,
    #             "name": product_attribute_value,
    #         }
    #     )
    #
    # def _search_or_create_product_attribute_line(
    #     self, product_template, product_attribute_color, product_attribute_color_value
    # ):
    #     result = self.env["product.template.attribute.line"].search(
    #         [
    #             ("product_tmpl_id", "=", product_template.id),
    #             ("attribute_id", "=", product_attribute_color.id),
    #             ("value_ids", "in", product_attribute_color_value.id),
    #         ]
    #     )
    #     if result:
    #         return result
    #
    #     result = self.env["product.template.attribute.line"].search(
    #         [
    #             ("product_tmpl_id", "=", product_template.id),
    #             ("attribute_id", "=", product_attribute_color.id),
    #         ]
    #     )
    #     if result and product_attribute_color_value not in result.value_ids:
    #         result.write({
    #             "value_ids": [(4, product_attribute_color_value.id)]
    #         })
    #         return result
    #
    #     result = self.env["product.template.attribute.line"].create(
    #         {
    #             "product_tmpl_id": product_template.id,
    #             "attribute_id": product_attribute_color.id,
    #             "value_ids": [(6, 0, [product_attribute_color_value.id])],
    #         }
    #     )
    #     return result
    #
    # def _update_product_product(self, product_template, product_attribute_value, standard_price, image):
    #     for product in product_template:
    #         product_variant = self.env["product.product"].search(
    #             [
    #                 ("product_tmpl_id", "=", product.id),
    #                 ("product_template_variant_value_ids.name", "=", product_attribute_value),
    #             ]
    #         )
    #
    #         print("*"*80)
    #         print("product.name: ", product.name)
    #         print("product_attribute_value: ", product_attribute_value)
    #         print("*"*80)
    #
    #         if product_variant:
    #             product_variant.write({
    #                 "standard_price": standard_price,
    #                 "default_code": product.name + " " + str(product_attribute_value),
    #             })
    #             if image:
    #                 print("*"*80)
    #                 print("image: ", image)
    #                 product_variant.write({
    #                     'image_1920': base64.b64encode(requests.get(image.strip()).content)
    #                         .replace(b'\n', b''),
    #                 })
    #
    # def _search_or_create_seller_in_product_template(self, product_template, seller):
    #     res_partner = self.env["res.partner"].search([("name", "=", seller.strip())])
    #     if not res_partner:
    #         res_partner = self.env["res.partner"].create(
    #             {
    #                 "name": seller,
    #                 "supplier_rank": 1,
    #             }
    #         )
    #     product_supplierinfo = self.env["product.supplierinfo"].search(
    #         [
    #             ("partner_id", "=", res_partner.id),
    #             ("product_tmpl_id", "=", product_template.id),
    #         ]
    #     )
    #     if not product_supplierinfo:
    #         self.env["product.supplierinfo"].create(
    #             {
    #                 "partner_id": res_partner.id,
    #                 "product_tmpl_id": product_template.id,
    #             }
    #         )
