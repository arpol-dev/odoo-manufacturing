# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, _

class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template"]

    def append_needs(self, table_needs, qty): 
        if self.bom_ids:
            stock = (0 if self.bom_ids.type == 'phantom' else self.virtual_available)                
            for item in self.bom_ids[0].bom_line_ids:
                product = item.product_tmpl_id
                table_needs = product.append_needs(table_needs, (qty-stock)*item.product_qty)
        else :
            if self.id not in table_needs:
                table_needs[self.id] = {'need': qty, 'stock': self.virtual_available}
            else:
                table_needs[self.id]['need'] += qty
        return table_needs
