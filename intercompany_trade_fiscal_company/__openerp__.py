# coding: utf-8
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Intercompany Trade - Fiscal Company',
    'version': '8.0.1.0.0',
    'category': 'Intercompany Trade',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base_fiscal_company',
        'intercompany_trade_base',
        'purchase',
        'sale',
        'simple_tax_account',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/view_account_account.xml',
        'views/view_fiscal_company_transcoding_account.xml',
        'views/view_intercompany_trade_config.xml',
        'views/view_res_company.xml',
    ],
    'demo': [
        'demo/account_tax.xml',
        'demo/account_account.xml',
        'demo/res_company.xml',
        'demo/fiscal_company_transcoding_account.xml',
        'demo/res_users.xml',
        'demo/res_groups.xml',
        'demo/intercompany_trade_config.xml',
        'demo/product_product.xml',
    ],
    'auto_install': True,
    'installable': True,
}
