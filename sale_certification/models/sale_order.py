from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    certification_ids = fields.One2many(
        "order.certification", 
        "order_id", 
        string="Certifications"
    )
    certifications_count = fields.Integer(
        string="Certifications Count", 
        compute="_compute_certifications_count"
    )
    total_certified = fields.Float(
        string="Total Certified", 
        compute="_compute_total_certified",
        help="Total of the certifications issued in the order"
    )

    @api.depends("certification_ids")
    def _compute_certifications_count(self):
        for order in self:
            order.certifications_count = len(order.certification_ids)

    def _compute_total_certified(self):
        for order in self:
            total = 0.0
            for cert in order.certification_ids:
                total += cert.total_certified
            order.total_certified = total

    def open_certify_wizard(self):
        self.ensure_one()
        return {
            "name": "Certify Order",
            "type": "ir.actions.act_window",
            "res_model": "certification.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id},
        }
