from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_copy_quantities(self):
        """ For qty_to_be_done value move to qty_done """
        for move_line in self.move_line_ids:
            if move_line.qty_done == 0.0:
                move_line.update(
                    {"qty_done": move_line.qty_to_be_done, "qty_to_be_done": 0.0}
                )
