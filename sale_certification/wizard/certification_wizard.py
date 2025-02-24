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
    certification_type = fields.Selection([
        ("chapters", "Chapters"),
        ("percentage", "Per Percentage"),
        ("regular", "Regular"),], 
        string="Certification Type", 
        default="regular",
        required=True,
    )
    sale_order_line_ids = fields.Many2many(
        "sale.order.line", 
        string="Sale Order Lines",
        domain="[('order_id', '=', order_id)]",
    )
    percentage = fields.Float(string="Percentage", default=0.0)

    @api.onchange("certification_type", "percentage")
    def _onchange_certification_type(self):
        if self.certification_type == "chapters":
            pass
        elif self.certification_type == "percentage":
            pass
        else:
            pass

    def action_create_certification(self):
        self.ensure_one()

        certification = self.env["order.certification"].create({
            "order_id": self.order_id.id,
            "name": self.name,
            "sequence": len(self.order_id.certification_ids) + 1,
        })

        if self.certification_type == "chapters":
            lines_to_certify = order.order_line.filtered(lambda l: l.display_type == "line_section" and not l.is_certified_chapter)
        elif self.certification_type == "percentage":
            total_lines = len(order.order_line)
            lines_to_certify = order.order_line[:int(total_lines * 0.5)]
        else:
            lines_to_certify = self.sale_order_line_ids

        for line in lines_to_certify:
            self.env["certification.line"].create({
                "certification_id": certification.id,
                "sale_line_id": line.id,
                "products": line.product_id.name if line.product_id else line.name,
                "quantity": line.certifiable_quantity,
                "certify_type": "line" if line.display_type is None else "section",
            })

        return {"type": "ir.actions.act_window_close"}