# Copyright 2024 ArPol
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = ['sale.order']

    simulation_line_ids = fields.One2many(
        comodel_name='sale.simulation.line',
        inverse_name='order_id',
        string='Lignes de simulation',
        compute='_compute_simulation',
        copy=False)
    
    missing_component_ids = fields.One2many(
        comodel_name='sale.missing.line',
        inverse_name='order_id',
        string='Lignes de composants manquants',
        compute='_compute_missing',
        copy=False)
    
    def _compute_simulation(self):
        for line in so.order_line:
            if line.product_template_id.bom_ids :
                vals = {
                    'order_id': self.id,
                    'order_line_id': line.id,
                    'product_template_id': line.product_template_id.id,
                    'simulation_qty': line.product_uom_qty,
                }
                self.env['sale.simulation.line'].create(vals)

    def _compute_missing(self):
        self.missing_component_ids.unlink()
        missing = []
        for line in so.order_line:
            product_id = line.product_template_id
            sale_needed = product_id.product_uom_qty - product_id.virtual_available
            if product_id.bom_ids & sale_needed > 0:
                for comp in product_id.bom_ids[0].bom_line_ids:
                    stock_needed = sale_needed * comp.product_qty
                    missing["Component_%s" % comp.product_id.id]['order_id'] = self.id
                    missing["Component_%s" % comp.product_id.id]['product_template_id'] = comp.product_id.id
                    missing["Component_%s" % comp.product_id.id]['simulation_qty'] += stock_needed
                        
        for line in missing:
            product = self.env['product_template'].search([('id','=',line['product_template_id'])])
            vals = {
                'order_id': line['order_id'],
                'product_template_id': line['product_template_id'],
                'simulation_qty': line['simulation_qty'],
                'virtual_qty': product.virtual_available,
                'missing_qty': line['simulation_qty'] - product.virtual_available
            }
            if vals['missing_qty'] > 0:
                self.env['sale.missing.line'].create(missing)        


class SaleSimulationLine(models.Model):
    _name = 'sale.simulation.line'
    _description = 'Ligne de simulation'
    _order = 'id asc'

    order_id = fields.Many2one('sale.order', string='Bon de commande')
    order_line_id = fields.Reference(
        string='Ligne de commande',
        selection='sale.order.line'
    )
    product_template_id = fields.Reference(string='Article', selection='product.template')
    simulation_qty = fields.Integer(string='Quantité à assembler')


class SaleMissingLine(models.Model):
    _name = 'sale.missing.line'
    _description = 'Ligne de composant manquant'
    _order = 'id asc'


    order_id = fields.Many2one('sale.order', string='Bon de commande')
    product_template_id = fields.Reference(string='Article', selection='product.template')
    virtual_qty = fields.Integer(string='Quantité prévue')
    simulation_qty = fields.Integer(string='Quantité recquise')
    missing_qty = fields.Integer(string='Quantité manquante')