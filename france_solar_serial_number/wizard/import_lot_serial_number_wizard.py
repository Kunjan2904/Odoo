# -*- coding: utf-8 -*-

import base64

from odoo import models, fields, _
from odoo.exceptions import UserError
from xlrd import open_workbook
from odoo.models import ValidationError


class ImportLotSerialNumber(models.TransientModel):
    _name = "import.lot.serial.number"
    _description = "To Show Import Serial/Lot Numbers"

    upload_file = fields.Binary(string=_("Attached Serial/Lot Numbers"))
    file_name = fields.Char(string=_("File Name"))

    def action_import_xlsx_file(self):
        """ Import Lot/Serial XLSX File and Create Record """
        context = self._context
        picking_id = self.env["stock.picking"].browse(context.get("picking_id"))
        product_id = self.env["product.product"].browse(context.get("product_id"))
        if (
            self.file_name
            and self.file_name.endswith(".xlsx")
            or self.file_name.endswith(".xls")
        ):
            file_data = base64.b64decode(self.upload_file)
            wb = open_workbook(file_contents=file_data)
            sheet = wb.sheet_by_index(0)
            values = sheet._cell_values
            picking = values[0][1].strip()
            product_code = values[1][1].strip()
            if not (picking and picking == picking_id.name):
                """Changed Warning"""
                raise UserError(_(" %s does not match or does not exist !" % picking))
            if not (product_code and product_code == product_id.default_code):
                raise UserError(
                    _("%s does not match or does not exist !" % product_code)
                )
            if values[4:]:
                for value in values[4:]:
                    serial_id, package_id, lot_id = False, False, False
                    if value[0] and not (value[1] or value[2]):
                        raise UserError(
                            _("Please add Lot or Serial number for import packages !")
                        )
                    if value[0]:
                        package = str(value[0]).replace(".0", "").strip()
                        package_id = self.env["stock.quant.package"].search(
                            [("name", "=", package)]
                        )
                        if not package_id:
                            package_id = self.env["stock.quant.package"].create(
                                {"name": package}
                            )
                    if product_id.tracking == "lot" and value[1] and not value[2]:
                        lot_number = str(value[1]).replace(".0", "").strip()
                        existing_lot = self.env["stock.lot"].search(
                            [
                                ("product_id", "=", product_id.id),
                                ("name", "=", lot_number),
                                (
                                    "company_id",
                                    "in",
                                    context.get("allowed_company_ids"),
                                ),
                            ]
                        )
                        if existing_lot:
                            lot_id = existing_lot
                        else:
                            lot_id = self.env["stock.lot"].create(
                                {
                                    "name": lot_number,
                                    "product_id": product_id.id,
                                    "company_id": self.env.company.id,
                                }
                            )
                    elif product_id.tracking == "serial" and value[2] and not value[1]:
                        serial_number = str(value[2]).replace(".0", "").strip()
                        if value[3] > 1:
                            raise ValidationError("For Products Tracked By Serial Numbers, The Quantity Should Not Exceed 1")
                        existing_serial = self.env["stock.lot"].search(
                            [
                                ("product_id", "=", product_id.id),
                                ("name", "=", serial_number),
                                (
                                    "company_id",
                                    "in",
                                    context.get("allowed_company_ids"),
                                ),
                            ]
                        )
                        if existing_serial:
                            serial_id = existing_serial
                        else:
                            serial_id = self.env["stock.lot"].create(
                                {
                                    "name": serial_number,
                                    "product_id": product_id.id,
                                    "company_id": self.env.company.id,
                                }
                            )
                    else:
                        if product_id.tracking in ["lot", "serial"] and not (
                            value[1] or value[2]
                        ):

                            raise UserError(_("Lot/Serial number is missing in lines!"))
                        else:
                            raise UserError(
                                _(
                                    "User assign lot or serial number is different from the product tracking!"
                                )
                            )
                    if lot_id and not picking_id.move_line_ids.filtered(
                        lambda ml: ml.lot_id == lot_id
                    ):
                        picking_id.update(
                            {
                                "move_line_ids": [
                                    (
                                        0,
                                        0,
                                        {
                                            "qty_to_be_done": value[3],
                                            "product_id": product_id.id,
                                            "lot_id": lot_id.id,
                                            "lot_name": lot_id.name,
                                            "result_package_id": package_id.id
                                            if package_id
                                            else False,
                                        },
                                    )
                                ]
                            }
                        )

                    if serial_id and not picking_id.move_line_ids.filtered(
                        lambda ml: ml.lot_id == serial_id
                    ):
                        picking_id.update(
                            {
                                "move_line_ids": [
                                    (
                                        0,
                                        0,
                                        {
                                            "qty_to_be_done": value[3] or 1.0,
                                            "product_id": product_id.id,
                                            "lot_id": serial_id.id,
                                            "lot_name": serial_id.name,
                                            "result_package_id": package_id.id
                                            if package_id
                                            else False,
                                        },
                                    )
                                ]
                            }
                        )
                return {
                    "name": "Detailed Operations",
                    "type": "ir.actions.act_window",
                    "res_model": "stock.move",
                    "view_mode": "form",
                    "view_id": self.env.ref(
                        "stock.view_stock_move_nosuggest_operations"
                    ).id,
                    "target": "new",
                    "res_id": self._context.get("active_id"),
                    "context": dict(
                        self.env.context,
                        show_lots_m2o=picking_id.has_tracking != "none"
                        and (
                            picking_id.picking_type_id.use_existing_lots
                            or picking_id.state == "done"
                        ),
                    ),
                }
            else:
                raise UserError(_("Please Add Serial or Lot Data In File ! "))
        else:
            raise UserError(_("Only .xlsx or .xls files can be imported"))
