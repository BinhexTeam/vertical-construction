from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    certification_ids = fields.One2many(
        "order.certification", "sale_order_id", string="Certifications"
    )

    def action_certify(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Certify Order",
            "res_model": "sale.order.certify.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_sale_order_id": self.id},
        }
