from odoo import fields, models


class SaleOrderCertifyWizard(models.TransientModel):
    _name = "sale.order.certify.wizard"
    _description = "Wizard para certificar la orden de venta"

    sale_order_id = fields.Many2one("sale.order", string="Sale Order", required=True)
    certificate_id = fields.Selection(
        selection=[("cert1", "Certification 1"), ("cert2", "Certification 2")],
        string="Certificate",
        required=True,
    )

    percentage = fields.Float(string="Certification Percentage", required=True)

    def action_apply_certification(self):
        return {"type": "ir.actions.act_window_close"}
