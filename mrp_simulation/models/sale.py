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
        logging.warning('remove simulation')
        existing = self.env['sale.simulation.line'].search([('order_id','=',self.id)])
        existing.unlink()
        logging.warning('success')
        lines = []
        for line in self.order_line:          
            if line.product_template_id.bom_ids :
                vals = {
                    'order_id': self.id,
                    'order_line_id': line.id,
                    'product_template_id': line.product_template_id.id,
                    'virtual_qty': line.product_template_id.virtual_available,
                    'simulation_qty': line.product_uom_qty,
                }
                result = self.env['sale.simulation.line'].create(vals)   
                lines.append(result.id)             
        self.simulation_line_ids = [(6,1,lines)]

    def _compute_missing(self):
        existing = self.env['sale.missing.line'].search([('order_id','=',self.id)])
        existing.unlink()
        lines = []
        missing = {}
        for line in self.order_line:
            product_id = line.product_template_id
            sale_needed = line.product_uom_qty - product_id.virtual_available
            if product_id.bom_ids and sale_needed > 0:
                for comp in product_id.bom_ids[0].bom_line_ids:
                    stock_needed = sale_needed * comp.product_qty
                    if comp.product_tmpl_id.id not in missing:
                        missing[comp.product_tmpl_id.id] = {
                            'order_id': self.id,
                            'product_template_id': comp.product_tmpl_id.id,
                            'simulation_qty': 0  # Initialisez la quantité simulée à zéro
                    }
                    # Mettre à jour la quantité simulée pour le composant
                    missing[comp.product_tmpl_id.id]['simulation_qty'] += stock_needed
               
        for line in missing.items():
            product = self.env['product.template'].search([('id','=',line[1]['product_template_id'])])
            vals = {
                'order_id': line[1]['order_id'],
                'product_template_id': line[1]['product_template_id'],
                'simulation_qty': line[1]['simulation_qty'],
                'virtual_qty': product.virtual_available,
                'missing_qty': line[1]['simulation_qty'] - product.virtual_available
            }
            if vals['missing_qty'] > 0:
                result = self.env['sale.missing.line'].create(vals) 
                lines.append(result.id)  
        self.missing_component_ids = [(6,1,lines)]
        self.write({'missing_component_ids': self.missing_component_ids})
        logging.warning('end')


class SaleSimulationLine(models.Model):
    _name = 'sale.simulation.line'
    _description = 'Ligne de simulation'
    _order = 'id asc'

    order_id = fields.Many2one('sale.order', string='Bon de commande')
    order_line_id = fields.Many2one('sale.order.line', string='Ligne de commande')
    product_template_id = fields.Many2one('product.template', string='Article')
    virtual_qty = fields.Integer(string='Quantité disponible ou prévue')
    simulation_qty = fields.Integer(string='Quantité à assembler')


class SaleMissingLine(models.Model):
    _name = 'sale.missing.line'
    _description = 'Ligne de composant manquant'
    _order = 'id asc'


    order_id = fields.Many2one('sale.order', string='Bon de commande')
    product_template_id = fields.Many2one('product.template', string='Article')
    virtual_qty = fields.Integer(string='Quantité prévue')
    simulation_qty = fields.Integer(string='Quantité recquise')
    missing_qty = fields.Integer(string='Quantité manquante')