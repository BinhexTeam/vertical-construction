from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_certified = fields.Boolean(
        string="Certified", 
        compute="_compute_is_certified"
    )
    is_certified_chapter = fields.Boolean(
        string="Chapter Certified", 
        compute="_compute_is_certified_chapter"
    )
    certifiable_quantity = fields.Float(
        string="Certifiable Quantity", 
        compute="_compute_certifiable_quantity"
    )
    cumulative_certified = fields.Float(
        string="Cumulative Certified", 
        compute="_compute_cumulative_certified", 
        help="Sum of the quantities certified for this line"
    )
    cumulative_certified_percentage = fields.Float(
        string="Cumulative Certified (%)", 
        compute="_compute_cumulative_certified", 
        help="Sum of the certified percentages of this line"
    )

    @api.depends("product_uom_qty", "qty_delivered", "qty_invoiced")
    def _compute_certifiable_quantity(self):
        for line in self:
            line.certifiable_quantity = line.product_uom_qty - line.qty_delivered - line.qty_invoiced

    def _compute_cumulative_certified(self):
        CertificationLine = self.env["certification.line"]
        for line in self:
            cert_lines = CertificationLine.search([("sale_line_id", "=", line.id)])
            total_certified = sum(cert.quantity for cert in cert_lines)
            total_percentage = sum(cert.relative_percentage for cert in cert_lines)
            line.cumulative_certified = total_certified
            line.cumulative_certified_percentage = total_percentage

    def _compute_is_certified(self):
        CertificationLine = self.env["certification.line"]
        for line in self:
            line.is_certified = bool(CertificationLine.search([("sale_line_id", "=", line.id)], limit=1))

    def _compute_is_certified_chapter(self):
        CertificationLine = self.env["certification.line"]
        for line in self:
            if line.display_type == "line_section":
                line.is_certified_chapter = bool(CertificationLine.search([
                    ("sale_line_id", "=", line.id),
                    ("certify_type", "=", "section")
                ], limit=1))
            else:
                line.is_certified_chapter = False

    def prepare_certification_values(self):
        return {
            "service": self.name,
            "quantity": self.certifiable_quantity,
            "type": "line",
        }
