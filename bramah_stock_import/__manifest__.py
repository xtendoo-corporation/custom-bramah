# Copyright 2023 Camilo Prado (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Importador de stock Bramah",
    "version": "16.0",
    "author": "Dani Domínguez(https://xtendoo.es)",
    "category": "Bramah",
    "license": "AGPL-3",
    "depends": [
        "product",
        "stock",
    ],
    "data": [
        "wizard/import_stock_wizard_view.xml",
        "views/stock_quant.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'active': False,
}
