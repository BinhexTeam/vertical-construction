from odoo import api, fields, models


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
    percentage = fields.Float(string="Percentage", default=0.0)
    sale_order_line_ids = fields.Many2many(
        "sale.order.line",
        "cert_wizard_sale_order_line_rel",
        "wizard_id", "line_id",
        string="Order Lines",
        domain=""" [
            ('order_id', '=', order_id), 
            ('is_certified', '=', False), 
            ('display_type', '=', False)
        ]
        """
    )
    chapter_ids = fields.Many2many(
        "sale.order.line",
        "cert_wizard_chapter_ids_rel",
        "wizard_id", "line_id",
        string="Chapters",
        domain="""[
            ('order_id', '=', order_id),
            ('is_certified_chapter', '=', False),
            ('display_type', '=', 'line_section')
        ]
        """
    )

    def action_create_certification(self):
        self.ensure_one()

        certification = self.env["order.certification"].create({
            "order_id": self.order_id.id,
            "name": self.name,
            "sequence": len(self.order_id.certification_ids) + 1,
        })

        action = self.env["ir.actions.actions"]._for_xml_id("sale_certification.order_certification_action")
        form_view = self.env.ref("sale_certification.view_order_certifications_form")
        action["views"] = [(form_view.id, "form")]
        action["res_id"] = certification.id

        if self.certification_type == "chapters":
            selected_chapters = self.chapter_ids.sorted(key=lambda r: r.sequence)
            for chapter in selected_chapters:
                chapter.is_certified_chapter = True
                self._certify_lines_for_chapter(certification, chapter)
        else:
            for line in self.sale_order_line_ids:
                line.is_certified = True
                self.env["certification.line"].create({
                    "certification_id": certification.id,
                    "sale_line_id": line.id,
                    "products": line.product_id.name if line.product_id else line.name,
                    "quantity": line.certifiable_quantity,
                    "certify_type": "line",
                    "section": "",
                })
               

        return action

    def _certify_lines_for_chapter(self, certification, chapter):
        sale_lines = self.order_id.order_line.sorted(key=lambda l: l.sequence)
        for line in sale_lines:
            if line.sequence <= chapter.sequence:
                continue

            if line.display_type == "line_section" and line not in self.chapter_ids:
                break

            if line.display_type == "line_note":
                continue

            self.env["certification.line"].create({
                "certification_id": certification.id,
                "sale_line_id": line.id,
                "products": line.product_id.name if line.product_id else line.name,
                "quantity": line.certifiable_quantity,
                "certify_type": "line",
                "section": chapter.name,
            })

            line.is_certified = True

