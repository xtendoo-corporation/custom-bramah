# Copyright 2023 Camilo Prado (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Importador de productos y proveedores Bramah",
    "version": "16.0",
    "author": "Manuel Calero, Dani Domínguez (https://xtendoo.es)",
    "category": "Calatayud",
    "license": "AGPL-3",
    "depends": [
        "product",
        "stock",
        "sale",
        "purchase",
    ],
    "data": [
        "wizard/import_product_wizard_view.xml",
        "views/bramah_product_import_view.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'active': False,
}
