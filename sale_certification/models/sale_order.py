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
    certified_percentage = fields.Float(
        string="Certified Lines (%)",
        compute="_compute_certified_percentage",
        store=True,
        digits=(16, 2),
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

    @api.depends("order_line.is_certified")
    def _compute_certified_percentage(self):
        for order in self:
            product_lines = order.order_line.filtered(lambda l: not l.display_type)
            total_lines = len(product_lines)
            
            if total_lines:
                certified_lines = product_lines.filtered(lambda l: l.is_certified)
                order.certified_percentage = (len(certified_lines) / total_lines) * 100.0
            else:
                order.certified_percentage = 0.0


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
