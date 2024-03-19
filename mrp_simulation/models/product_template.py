# Copyright 2018 Nicolas JEUDY
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import datetime
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = ['event.event']

    duration_hour = fields.Float('Duration in hour(s)')
    learning_id = fields.Many2one('product.template', string='Learning', domain=[('is_learning', '=', True)])
    date_text= fields.Char("Date in text mode")
    hour_text= fields.Char("Training time")
    duration_days = fields.Float(related='learning_id.duration_days', store=True )
    methodology_partner_id = fields.Many2one('res.partner', "Methodology partner")
    
class EventRegistration(models.Model):
    _inherit = 'event.registration'

    is_learning = fields.Boolean(related='event_id.learning_id.is_learning', readonly="1", store=True)

class EventTicket(models.Model):
    _inherit = 'event.event.ticket'

    @api.model
    def default_get(self, fields):
        res = super(EventTicket, self).default_get(fields)
        product_tmpl_id = self.env.context.get('learning_id', False)
        if product_tmpl_id:
            product_id = self.env['product.product'].search(
                [('product_tmpl_id', '=', product_tmpl_id)],
                limit=1
            )
            if product_id:
                res['product_id'] = product_id.id
        return res
