import datetime
from collections import OrderedDict

from odoo import api, models, fields



class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends('stock_valuation_layer_ids')
    @api.depends_context('to_date', 'company')
    def _compute_value_svl(self):
        """Compute totals of multiple svl related values"""
        company_id = self.env.company
        self.company_currency_id = company_id.currency_id
        domain = [
            ('product_id', 'in', self.ids),
            ('company_id', '=', company_id.id),
        ]
        if self.env.context.get('to_date'):
            to_date = fields.Datetime.to_datetime(self.env.context['to_date'])
            domain.append(('create_date', '<=', to_date))
        groups = self.env['stock.valuation.layer']._read_group(domain, ['value:sum', 'quantity:sum'], ['product_id'])
        products = self.browse()
        # Browse all products and compute products' quantities_dict in batch.
        self.env['product.product'].browse([group['product_id'][0] for group in groups]).sudo(False).mapped(
            'qty_available')
        for group in groups:
            product = self.browse(group['product_id'][0])
            value_svl = company_id.currency_id.round(group['value'])
            avg_cost = value_svl / group['quantity'] if group['quantity'] else 0
            product.value_svl = value_svl
            product.quantity_svl = group['quantity']
            product.avg_cost = avg_cost
            product.total_value = avg_cost * product.sudo(False).qty_available
            products |= product
        remaining = (self - products)
        if len(remaining) > 0:
            for product in remaining:
                product.value_svl = company_id.currency_id.round(product.standard_price)
                product.quantity_svl = self.env['product.product'].browse(product.id).qty_available
                product.avg_cost = company_id.currency_id.round(product.standard_price)
                product.total_value = product.avg_cost * product.quantity_svl
