# coding: utf-8
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.tools import config as tools_config
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # TODO V10. Check if it is required with workflow removing
    # Alternatively, we could add a check on the user. (Block if user != admin)
    _CUSTOMER_ALLOWED_FIELDS = [
        'state', 'date_due', 'period_id', 'move_id', 'move_name',
        'internal_number',
    ]

    # Columns Section
    intercompany_trade = fields.Boolean(
        string='Intercompany Trade', related='partner_id.intercompany_trade',
        store=True)

    intercompany_trade_readonly = fields.Boolean(
        string='Intercompany Trade Readonly',
        compute='_compute_intercompany_trade_readonly')

    # Compute Section
    @api.multi
    @api.depends('type', 'intercompany_trade')
    def _compute_intercompany_trade_readonly(self):
        for invoice in self.filtered(
                lambda x: x.intercompany_trade and
                x.type in ['in_invoice', 'in_refund']):
            invoice.intercompany_trade_readonly = True

    # Overload Section
    @api.model
    def create(self, vals):
        invoice = super(AccountInvoice, self).create(vals)
        invoice._check_intercompany_trade_write(vals)
        return invoice

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        self._check_intercompany_trade_write(vals)
        return res

    @api.multi
    def invoice_validate(self):
        for invoice in self.filtered(
                lambda x: x.intercompany_trade and 'out_' in x.type):
            invoice._create_intercompany_invoice()
        return super(AccountInvoice, self).invoice_validate()

    # Custom Section
    @api.multi
    def _check_intercompany_trade_write(self, vals):
        # check if the operation is done in by a intercompany trade
        # process
        if self.env.context.get('intercompany_trade_create', False):
            return

        # Check if it s about a allowed fields
        copy_vals = vals.copy()
        for key in self._CUSTOMER_ALLOWED_FIELDS:
            copy_vals.pop(key, False)
        if not copy_vals:
            return

        for invoice in self.filtered(lambda x: x.intercompany_trade):
            if 'in_' in invoice.type:
                raise UserError(_(
                    "You can not create a supplier invoice or refund"
                    " for intercompany trade supplier. Please ask to"
                    " your supplier to create or update it"))

    @api.multi
    def _create_intercompany_invoice(self):
        AccountInvoiceLine = self.env['account.invoice.line']
        self.ensure_one()
        config = self._get_intercompany_trade_config_by_partner_company_type()
        invoice_vals = self._prepare_intercompany_vals(config)
        # Create Customer invoice
        customer_invoice = self.sudo(
            config.customer_user_id).with_context(
                intercompany_trade_create=True).create(invoice_vals)

        # Create lines
        for invoice_line in self.invoice_line:
            line_vals = invoice_line._prepare_intercompany_vals(
                config, customer_invoice)
            # TODO: V10 Check if it is mandatory to use suspend_security()
            # TODO: V10, check if suspend_security() is better implemented
            # for the time being, doesn't work in test part.
            if tools_config.get('test_enable', False):
                AccountInvoiceLine.sudo().with_context(
                    force_company=config.customer_company_id.id,
                    intercompany_trade_create=True).create(
                        line_vals)
            else:
                AccountInvoiceLine.sudo(
                    config.customer_user_id).suspend_security().with_context(
                        intercompany_trade_create=True).create(
                            line_vals)

        # Reset Taxes
        customer_invoice.sudo(
            config.customer_user_id).with_context(
                intercompany_trade_create=True).button_reset_taxes()

        for field_name in ['amount_untaxed', 'amount_tax', 'amount_total']:
            supplier_value = getattr(self, field_name)
            customer_value = getattr(customer_invoice, field_name)
            if supplier_value != customer_value:
                raise UserError(_(
                    "Unable to confirm this intercompany Trade invoice (or"
                    " refund) because the field '%s' is not the same: \n"
                    " - customer value : %s\n"
                    " - supplier value : %s") % (
                        field_name, customer_value, supplier_value))

        # Confirm Customer invoice
        customer_invoice.sudo(
            config.customer_user_id).with_context(
                intercompany_trade_create=True).signal_workflow('invoice_open')

    @api.multi
    def _get_intercompany_trade_config_by_partner_company_type(self):
        config_obj = self.env['intercompany.trade.config']

        self.ensure_one()
        if self.type in ('in', 'in_invoice', 'in_refund'):
            regular_type = 'in'
        else:
            regular_type = 'out'

        return config_obj._get_intercompany_trade_by_partner_company(
            self.partner_id.id, self.company_id.id, regular_type)

    @api.multi
    def _prepare_intercompany_vals(self, config):
        self.ensure_one()
        customer_user = config.customer_user_id
        other_company_id = config.customer_company_id.id
        other_partner_id = config.supplier_partner_id.id
        if self.type == 'out_invoice':
            # A Sale Invoice Create a Purchase Invoice
            other_type = 'in_invoice'
        elif self.type == 'out_refund':
            # A Sale Refund Create a Purchase Refund
            other_type = 'in_refund'

        account_info = self.sudo(customer_user).onchange_partner_id(
            other_type, other_partner_id, company_id=other_company_id)['value']

        account_journal = self.sudo(customer_user).with_context(
            type=other_type, company_id=other_company_id)._default_journal()

        return {
            'type': other_type,
            'company_id': other_company_id,
            'date_invoice': self.date_invoice,
            'date_due': self.date_due,
            'currency_id': self.currency_id.id,
            'comment': self.comment,
            'supplier_invoice_number': self.number,
            'partner_id': other_partner_id,
            'account_id': account_info['account_id'],
            'journal_id': account_journal.id,
        }

    # # required ?
    # amount_total = fields.Float(compute_sudo=True)

    # amount_tax = fields.Float(compute_sudo=True)

    # amount_untaxed = fields.Float(compute_sudo=True)

    # Overload Section
    # @api.model
    # def create(self, vals):
    #     partner_obj = self.env['res.partner']
    #     partner = partner_obj.browse(vals['partner_id'])

    #     create_account_invoice = (not self.env.context.get(
    #         'intercompany_trade_do_not_propagate', False) and
    #         partner.intercompany_trade)

    #     if create_account_invoice:
    #         line_ids = vals.get('invoice_line', False)
    #         vals.pop('invoice_line', None)

    #     invoice = super(AccountInvoice, self).create(vals)

    #     if create_account_invoice and\
    #             invoice.type in ['in_invoice', 'in_refund']:
    #         raise UserError(_(
    #             "You can not create a Purchase invoice or refund for "
    #             " intercompany trade. Ask to your supplier to create it."))

    #     if create_account_invoice:
    #         # Get config
    #         config = self._get_intercompany_trade_by_partner_company_type(
    #             invoice.partner_id.id, invoice.company_id.id, invoice.type)

    #         # Create associated Invoice
    #         invoice_other_vals, other_user =\
    #             invoice.prepare_intercompany_invoice(config, 'create')

    #         invoice_other = self.sudo().with_context(
    #             intercompany_trade_do_not_propagate=True).create(
    #             invoice_other_vals)

    #         # Set other id
    #         invoice.write({
    #             'intercompany_trade_account_invoice_id': invoice_other.id,
    #         })

    #         # Update Proper Account Invoice
    #         invoice.write({
    #             'invoice_line': line_ids,
    #         })

    #     return invoice

    # TODO FORBID state change for customer
    # TODO refactor state management (verify state) or wait for V10
    # @api.multi
    # def write(self, vals):
    #     res = super(AccountInvoice, self).write(vals)

    #     if not self.env.context.get(
    #             'intercompany_trade_do_not_propagate', False):

    #         for invoice in self.filtered(lambda x: x.intercompany_trade):
    #             if vals.get('state', False) == 'cancel':
    #                 raise UserError(_(
    #                     "You can not cancel intercompany Trade. Please make"
    #                     " a Refund."))
    #             if invoice.type in ['in_invoice', 'in_refund']:
    #                 copy_vals = vals.copy()
    #                 for key in self._CUSTOMER_ALLOWED_FIELDS:
    #                     copy_vals.pop(key, False)
    #                 if copy_vals:
    #                     raise UserError(_(
    #                         "You can not write a Purchase invoice or refund"
    #                         " for intercompany trade. Ask to your supplier"
    #                         " to create it.\n\n %s") % ', '.join(
    #                             [x for x in copy_vals.keys()]))
    #                 continue

    #             config =\
    #                 self._get_intercompany_trade_by_partner_company_type(
    #                     invoice.partner_id.id, invoice.company_id.id,
    #                     invoice.type)
    #             # Disable possibility to change the supplier
    #             if 'partner_id' in vals and\
    #                     vals.get('partner_id') != invoice.partner_id.id:
    #                 raise UserError(_(
    #                     "Error!\nYou can not change the partner because of"
    #                     " Intercompany Trade Rules. Please create"
    #                     " a new Invoice."))

    #             # Update changes for according invoice
    #             invoice_vals, other_user =\
    #                 invoice.prepare_intercompany_invoice(config, 'update')

    #             invoice_other = invoice.sudo().browse(
    #                 invoice.intercompany_trade_account_invoice_id)
    #             invoice_other.with_context(
    #                 intercompany_trade_do_not_propagate=True).write(
    #                     invoice_vals)

    #             # Check during State changes if amount are coherent
    #             if vals.get('state', False):
    #                 if invoice_other.amount_untaxed !=\
    #                         invoice.amount_untaxed\
    #                         or invoice_other.amount_tax !=\
    #                         invoice.amount_tax:
    #                     raise UserError(_(
    #                         "Error!\nYou can not change the state of this"
    #                         " invoice because the according customer invoice"
    #                         " doesn't have the same total amount."
    #                         " Please fix the problem first."))

    #             if vals.get('state', False) == 'open':
    #                 invoice_other.sudo().signal_workflow('invoice_open')

    #     return res

    # @api.multi
    # def unlink(self):
    #     if not self.env.context.get(
    #             'intercompany_trade_do_not_propagate', False):

    #         for invoice in self.filtered(lambda x: x.intercompany_trade):
    #             # Block Customer Deletion
    #             if invoice.type in ('in_invoice', 'in_refund'):
    #                 raise UserError(_(
    #                     "Error!\nYou can not delete invoices."
    #                     " Please ask to your supplier to do it."))

    #             # Delete according Invoice
    #             invoice_other = invoice.sudo().browse(
    #                 invoice.intercompany_trade_account_invoice_id)
    #             invoice_other.with_context(
    #                 intercompany_trade_do_not_propagate=True).unlink()

    #     return super(AccountInvoice, self).unlink()
