# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Intercompany Trade - Base",
    "version": "12.0.1.0.3",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "http://www.grap.coop",
    "license": "AGPL-3",
    "depends": ["base", "base_suspend_security"],
    "data": [
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/view_res_partner.xml",
        "views/view_intercompany_trade_config.xml",
    ],
    "demo": [
        "demo/res_company.xml",
        "demo/res_users.xml",
        "demo/res_groups.xml",
        "demo/res_partner.xml",
        "demo/intercompany_trade_config.xml",
    ],
    "installable": True,
}
