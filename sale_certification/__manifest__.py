{
    "name": "Sale Certification",
    "summary": "This module allows to certificate sales orders",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Binhex,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-construction",
    "category": "Sales",
    "depends": [
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/view_order_form_certify.xml",
        "wizard/sale_order_certify.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "icon": "",
}
