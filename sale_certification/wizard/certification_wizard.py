from odoo import fields, models


class CertificationWizard(models.TransientModel):
    _name = "certification.wizard"
    _description = "Modal to Certify an Order"

    order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        required=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    certification_type = fields.Selection(
        [
            ("chapters", "Chapters"),
            ("percentage", "Per Percentage"),
            ("regular", "Regular"),
        ],
        string="Certification Type",
        default="regular",
        required=True,
    )
    sale_order_line_ids = fields.Many2many(
        "sale.order.line",
        string="Order Lines",
        domain="""
            [
                ('order_id', '=', order_id),
                ('is_certified', '=', False),
                ('is_certified_chapter', '=', False),
                ('display_type', '=', certification_type == 'chapters' and 'line_section' or False),
                ('display_type', '!=', certification_type in ['percentage', 'regular'] and 'line_section' or False)
            ]
        """,
    )
    percentage = fields.Float(string="Percentage", default=0.0)

    # TODO Refactor this method and fix is_certified_chapter

    def action_create_certification(self):
        self.ensure_one()

        certification = self.env["order.certification"].create(
            {
                "order_id": self.order_id.id,
                "name": self.name,
                "sequence": len(self.order_id.certification_ids) + 1,
            }
        )

        for line in self.sale_order_line_ids:
            if line.display_type == "line_section":
                lines = self.env["sale.order.line"].search(
                    [
                        ("order_id", "=", self.order_id.id),
                        ("sequence", ">", line.sequence),
                    ]
                )

                self._certify_section_lines(lines, certification)

                if line == self.sale_order_line_ids[-1]:
                    break

            elif line.display_type == "line_note":
                continue
            else:
                self.env["certification.line"].create(
                    {
                        "certification_id": certification.id,
                        "sale_line_id": line.id,
                        "products": line.product_id.name
                        if line.product_id
                        else line.name,
                        "quantity": line.certifiable_quantity,
                        "certify_type": "line",
                    }
                )

                line.is_certified = True

        return {"type": "ir.actions.act_window_close"}

    def _certify_section_lines(self, lines, certification):
        for line in lines:
            if line.display_type == "line_section":
                # self.env["certification.line"].create({
                #     "certification_id": certification.id,
                #     "sale_line_id": line.id,
                #     "products": line.name,
                #     "quantity": line.certifiable_quantity,
                #     "certify_type": "section",
                # })

                line.is_certified_chapter = True  # When line is not created, fix to turn it false when deleting certification
                break

            if line.display_type is False:
                self.env["certification.line"].create(
                    {
                        "certification_id": certification.id,
                        "sale_line_id": line.id,
                        "products": line.product_id.name
                        if line.product_id
                        else line.name,
                        "quantity": line.certifiable_quantity,
                        "certify_type": "line",
                    }
                )

                line.is_certified = True
