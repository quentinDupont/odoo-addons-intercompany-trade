# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Account module for Odoo
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

from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from openerp.osv import fields
from openerp.osv.orm import Model

from openerp.addons.integrated_trade_product.model.custom_tools\
    import _get_other_product_info


class AccountInvoiceLine(Model):
    _inherit = 'account.invoice.line'

    # Columns Section
    _columns = {
        'integrated_trade': fields.related(
            'invoice_id', 'integrated_trade', type='boolean',
            string='Integrated Trade'),
        'integrated_trade_account_invoice_line_id': fields.many2one(
            'account.invoice.line',
            string='Integrated Trade Account Invoice Line',
            readonly=True,
        ),
    }

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        """Create the according Account Invoice Line."""
        ai_obj = self.pool['account.invoice']
        pp_obj = self.pool['product.product']
        ppl_obj = self.pool['product.pricelist']

        if vals.get('invoice_id', False):
            ai = ai_obj.browse(cr, uid, vals['invoice_id'], context=context)
            create_account_invoice_line = (
                not context.get('integrated_trade_do_not_propagate', False) and
                ai.integrated_trade)
        else:
            create_account_invoice_line = False

        # Call Super: Create
        res = super(AccountInvoiceLine, self).create(
            cr, uid, vals, context=context)

        if create_account_invoice_line:
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True

            rit = ai_obj._get_res_integrated_trade(
                cr, uid, ai.partner_id.id, ai.company_id.id, ai.type,
                context=context)

            if ai.type in ('in_invoice', 'in_refund'):
                direction = 'in'
                other_user_id = rit.supplier_user_id.id
                other_type = 'out_invoice'
                other_company_id = rit.supplier_company_id.id
                other_partner_id = rit.customer_partner_id.id
            else:
                direction = 'out'
                other_user_id = rit.customer_user_id.id
                other_type = 'in_invoice'
                other_company_id = rit.customer_company_id.id
                other_partner_id = rit.supplier_partner_id.id

            # Create according account invoice line
            other_product_info = _get_other_product_info(
                self.pool, cr, uid, rit, vals['product_id'], direction,
                context=context)

            ail_other_vals = self.product_id_change(
                cr, other_user_id, False, other_product_info['product_id'],
                False, type=other_type, company_id=other_company_id,
                partner_id=other_partner_id)['value']
            ail_other_vals.update({
                'invoice_id': ai.integrated_trade_account_invoice_id.id,
                'product_id': other_product_info['product_id'],
                'company_id': other_company_id,
                'partner_id': other_partner_id,
                'quantity': vals['quantity'],
                'uos_id': vals['uos_id'],
                'invoice_line_tax_id': [[
                    6, False, ail_other_vals['invoice_line_tax_id']]],
                })

            ail_other_id = self.create(
                cr, other_user_id, ail_other_vals, context=ctx)

            # if this is a supplier invoice and an integrated trade, the user
            # doesn't have the right to change the unit price, so we will
            # erase the unit price, and recover the good one.
            if ai.type in ('in_invoice', 'in_refund'):
                supplier_pp = pp_obj.browse(
                    cr, rit.supplier_user_id.id,
                    other_product_info['product_id'], context=context)
                price_unit = ppl_obj._compute_integrated_prices(
                    cr, rit.supplier_user_id.id, supplier_pp,
                    ai.partner_id, rit.pricelist_id,
                    context=None)['supplier_sale_price']
            else:
                price_unit = vals['price_unit']

            # Update Original Account Invoice Line
            self.write(cr, uid, res, {
                'integrated_trade_account_invoice_line_id': ail_other_id,
                'price_unit': price_unit,
            }, context=ctx)

            # Update Other Account Invoice Line
            self.write(
                cr, other_user_id, ail_other_id, {
                    'integrated_trade_account_invoice_line_id': res,
                    'price_unit': price_unit,
                }, context=ctx)

            # Recompute All Invoice
            ai_obj.button_reset_taxes(
                cr, uid, [ai.id], context=context)
            ai_obj.button_reset_taxes(
                cr, other_user_id, [ai.integrated_trade_account_invoice_id.id],
                context=context)

        return res

    def write(self, cr, uid, ids, vals, context=None):
        """"- Update the according Invoice Line with new data.
            - Block any changes of product.
            - the function will propagate only to according invoice line
              price or quantity changes. All others are ignored. Most of
              the important fields ignored will generated an error.
              (product / discount / UoM changes)    """
        context = context and context or {}
        ai_obj = self.pool['account.invoice']

        res = super(AccountInvoiceLine, self).write(
            cr, uid, ids, vals, context=context)

        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for ail in self.browse(cr, uid, ids, context=context):
                if ail.integrated_trade_account_invoice_line_id:
                    rit = ai_obj._get_res_integrated_trade(
                        cr, uid, ail.invoice_id.partner_id.id,
                        ail.invoice_id.company_id.id,
                        ail.invoice_id.type, context=context)

                    if ail.invoice_id.type in ('in_invoice', 'in_refund'):
                        other_user_id = rit.supplier_user_id.id
                    else:
                        other_user_id = rit.customer_user_id.id

                    if 'product_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the product. %s"""
                                """Please remove this line and choose a"""
                                """ a new one.""" % (ail.product_id.name)))
                    if 'discount' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not set a discount for integrated"""
                                """ Trade. Please change the Unit Price"""
                                """ of %s.""" % (ail.product_id.name)))
                    if 'uos_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the UoM of the Product"""
                                """ %s.""" % (ail.product_id.name)))
                    if 'price_unit' in vals.keys() and ail.invoice_id.type\
                            in ('in_invoice', 'in_refund'):
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the Unit Price of"""
                                """ '%s'. Please ask to your supplier.""" % (
                                    ail.product_id.name)))
                    other_vals = {}
                    if vals.get('quantity', False):
                        other_vals['quantity'] = vals['quantity']
                    if vals.get('price_unit', False):
                        other_vals['price_unit'] = vals['price_unit']

                    self.write(
                        cr, other_user_id,
                        ail.integrated_trade_account_invoice_line_id.id,
                        other_vals, context=ctx)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """"- Unlink the according Invoice Line."""
        ai_obj = self.pool['account.invoice']
        context = context and context or {}

        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for ail in self.browse(
                    cr, uid, ids, context=context):
                ai = ail.invoice_id
                rit = ai_obj._get_res_integrated_trade(
                    cr, uid, ai.partner_id.id, ai.company_id.id, ai.type,
                    context=context)
                if ail.invoice_id.type in ('in_invoice', 'in_refund'):
                    other_uid = rit.supplier_user_id.id
                else:
                    other_uid = rit.customer_user_id.id
                self.unlink(
                    cr, other_uid,
                    [ail.integrated_trade_account_invoice_line_id.id],
                    context=ctx)
        res = super(AccountInvoiceLine, self).unlink(
            cr, uid, ids, context=context)
        return res