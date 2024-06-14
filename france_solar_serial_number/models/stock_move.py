# -*- coding: utf-8 -*-

import base64
import xlsxwriter
import io

from odoo import models, fields,_
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def import_serial_number(self):
        """Open Import Serial/Lot Numbers Wizard"""
        new_context = self._context.copy()
        new_context.update(
            {"picking_id": self.picking_id.id, "product_id": self.product_id.id}
        )
        return {
            "name": "Import Serial/Lot Numbers",
            "type": "ir.actions.act_window",
            "res_model": "import.lot.serial.number",
            "view_mode": "form",
            "target": "new",
            "context": new_context,
        }

    def download_sample_file(self):
        """To Download Sample XLSX File For Import Lot/Serial Numbers"""
        picking = self.picking_id.name
        product_default_code = self.product_id.default_code

        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet()
        # Format
        bold_format = workbook.add_format({"bold": True})
        bold_red_format = workbook.add_format({"bold": True, "color": "red"})
        # Headers
        worksheet.write(0, 0, "Picking Name", bold_red_format)
        worksheet.set_column(0, 0, 15)
        worksheet.write(0, 1, picking)
        worksheet.set_column(0, 1, 15)
        worksheet.write(1, 0, "Product Ref", bold_red_format)
        worksheet.set_column(1, 0, 15)
        worksheet.write(1, 1, product_default_code)
        worksheet.write(3, 0, "Package", bold_format)
        worksheet.write(3, 1, "Lot Number", bold_format)
        worksheet.write(3, 2, "Serial Number", bold_format)
        worksheet.write(3, 3, "Quantity", bold_format)
        workbook.close()
        fp.seek(0)

        if not product_default_code:
            raise UserError(_(self.product_id.name + " Has No Internal Reference !"))
        else:
            attachment_id = self.env["ir.attachment"].create(
                {
                    "name": picking.replace("/", "-")
                    + "_["
                    + product_default_code
                    + "]_sample.xlsx",
                    "datas": base64.b64encode(fp.read()),
                }
            )
            download_url = "/web/content/" + str(attachment_id.id) + "?download=True"
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                "target": "new",
            }


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    qty_to_be_done = fields.Float(
        "Qty To be Done", default=0.0, digits="Product Unit of Measure", copy=False
    )
