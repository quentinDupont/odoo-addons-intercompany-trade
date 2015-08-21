# -*- encoding: utf-8 -*-
##############################################################################
#
#    Fiscal Company for Intercompany Trade Module for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'CIS - Intercompany Trade Fiscal Company',
    'version': '1.0',
    'category': 'CIS',
    'description': """
Manage specific intercompany trade for Cooperative
==================================================

Features :
----------
    * TOWRITE;

TODO :
------
    * Update the description of this module;

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2015-Today, Groupement Régional Alimentaire de Proximité;
    * Author :
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'account_fiscal_company',
        'intercompany_trade_base',
        'purchase',
        'sale',
        'stock',
        'simple_tax_account',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir_model_access.yml',
        'view/view.xml',
        'view/action.xml',
        'view/menu.xml',
    ],
    'demo': [
        'demo/account_tax.yml',
        'demo/account_account.xml',
        'demo/fiscal_company_transcoding_account.yml',
        'demo/res_users.yml',
        'demo/res_groups.yml',
        'demo/intercompany_trade_config.yml',
        'demo/product_product.yml',
        'demo/stock_location.yml',
        'demo/stock_warehouse.yml',
        'demo/sale_shop.yml',
        'demo/ir_values.xml',
        'demo/ir_values.yml',
    ],
    'auto_install': True,
}