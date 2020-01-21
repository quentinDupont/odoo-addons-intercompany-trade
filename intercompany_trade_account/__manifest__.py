# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Intercompany Trade - Account",
    "version": "12.0.1.0.0",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "http://www.grap.coop",
    "license": "AGPL-3",
    "depends": [
        "intercompany_trade_base",
        "base_suspend_security",
        "account",
    ],
    "demo": [
        "demo/account_fiscalyear.xml",
        "demo/account_period.xml",
        "demo/res_groups.xml",
        "demo/account_account.xml",
        "demo/account_journal.xml",
        "demo/ir_property.xml",
        "demo/account_tax.xml",
        "demo/product_product.xml",
        "demo/product_supplierinfo.xml",
        "demo/account_invoice.xml",
    ],
    "data": ["views/menu.xml", "views/view_account_invoice.xml",],
    "auto_install": True,
    "installable": True,
}
