# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT <quentin.dupont@grap.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        order_obj = self.env['purchase.order']
        order = order_obj.browse(self._context.get('active_id'))
        super(Picking, self).button_validate()
        if order.intercompany_trade:
            order.button_done()
            order.invoice_status = 'no'