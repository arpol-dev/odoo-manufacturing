# Copyright 2024 ArPol
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = ['sale.order']

    simulation_line_ids = fields.One2many(
        comodel_name='sale.simulation.line',
        inverse_name='order_id',
        string='Lignes de simulation',
        compute='_compute_simulation',
        store=False)
    
    missing_component_ids = fields.One2many(
        comodel_name='sale.missing.line',
        inverse_name='order_id',
        string='Lignes de composants manquants',
        compute='_compute_missing',
        store=False)

    @api.onchange('order_line')
    def _compute_simulation(self):
        # existing = self.env['sale.simulation.line'].search([('order_id','=',self.id)])
        # existing.unlink()
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
        self._compute_missing()

    def _compute_missing(self):
        lines = []
        needs = {} # Dict : {product_id: {'need': X, 'stock': Y}, etc}
        for line in self.simulation_line_ids:
            product = line.product_template_id
            needs = product.append_needs(needs, line.simulation_qty)

        for entry in needs.items():
            if entry[1]['need'] > entry[1]['stock']:
                vals = {
                    'order_id': self.id,
                    'product_template_id': entry[0],
                    'simulation_qty': entry[1]['need'],
                    'virtual_qty': entry[1]['stock'],
                    'missing_qty': entry[1]['need'] - entry[1]['stock']
                }
                result = self.env['sale.missing.line'].create(vals)
                lines.append(result.id)
                
        self.missing_component_ids = [(6,1,lines)]

    def print_simulation(self):
        return self.env.ref('mrp_simulation.print_simulation').report_action(self)


class SaleSimulationLine(models.TransientModel):
    _name = 'sale.simulation.line'
    _description = 'Ligne de simulation'
    _order = 'id asc'

    order_id = fields.Many2one('sale.order', string='Bon de commande')
    order_line_id = fields.Many2one('sale.order.line', string='Ligne de commande')
    product_template_id = fields.Many2one('product.template', string='Article')
    virtual_qty = fields.Integer(string='Quantité disponible ou prévue')
    simulation_qty = fields.Integer(string='Quantité à assembler')


class SaleMissingLine(models.TransientModel):
    _name = 'sale.missing.line'
    _description = 'Ligne de composant manquant'
    _order = 'id asc'


    order_id = fields.Many2one('sale.order', string='Bon de commande')
    product_template_id = fields.Many2one('product.template', string='Article')
    virtual_qty = fields.Integer(string='Quantité prévue')
    simulation_qty = fields.Integer(string='Quantité recquise')
    missing_qty = fields.Integer(string='Quantité manquante')