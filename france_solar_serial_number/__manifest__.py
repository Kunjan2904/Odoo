# -*- coding: utf-8 -*-

{
    "name": " France Solar Serial Number",
    "version": "16.0.1.1.0",
    "category": "Stock",
    "summary": "Stock/france_solar_serial_number",
    "author": "Kunjan Patel",
    "website": "",
    "sequence": 10,
    "description": """,
        Stock/france_solar_serial_number
    """,
    "depends": ["stock", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_move_view.xml",
        "views/stock_picking_view.xml",
        "wizard/import_lot_serial_number_wizard_view.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": True,
    "license": "LGPL-3",
}
