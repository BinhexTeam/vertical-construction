from odoo import models, fields, api

class CertificationLine(models.Model):
    _name = "certification.line"
    _description = "Certification Line"

    certification_id = fields.Many2one(
        "order.certification", 
        string="Certification", 
        required=True, 
        ondelete="cascade"
    )
    sale_line_id = fields.Many2one(
        "sale.order.line", 
        string="Sale Order Line", 
        required=True, 
        ondelete="cascade"
    )
    products = fields.Char(string="Product/Service")
    quantity = fields.Float(string="Certified Quantity")
    certify_type = fields.Selection([
        ("section", "Section"),
        ("note", "Note"),
        ("line", "Line"),
    ], string="Type", default="line")
    section = fields.Char(string="Section")
    relative_percentage = fields.Float(
        string="Relative Percentage", 
        compute="_compute_relative_percentage", 
        store=True,
        help="Percentage relative to the quantity in the sale order line"
    )

    @api.depends("quantity", "sale_line_id.product_uom_qty")
    def _compute_relative_percentage(self):
        for rec in self:
            if rec.sale_line_id and rec.sale_line_id.product_uom_qty:
                rec.relative_percentage = (rec.quantity / rec.sale_line_id.product_uom_qty) * 100
            else:
                rec.relative_percentage = 0.0