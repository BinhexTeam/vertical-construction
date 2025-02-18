from odoo import fields, models

CERTIFICATION_STATES = [
    ("draft", "Draft"),
    ("confirmed", "Confirmed"),
    ("cancel", "Cancelled"),
]

CERTIFICATION_METHODS = [
    ("sections", "Per Sections"),
    ("elements", "Per Elements"),
]


class OrderCertification(models.Model):
    _name = "order.certification"

    name = fields.Char(
        string="Certification Identifier",
        required=True,
        copy=False,
        readonly=True,
        default=0,
    )
    sale_order_id = fields.Many2one(
        "sale.order", string="Sale Order", required=True, ondelete="cascade"
    )
    certification_date = fields.Date(default=fields.Date.context_today)
    state = fields.Selection(CERTIFICATION_STATES, default="draft", tracking=True)
    certification_method = fields.Selection(CERTIFICATION_METHODS, required=True)
    total_certified_abs = fields.Float(
        string="Total Certified Absolute", compute="_compute_totals", store=True
    )
    total_certified_perc = fields.Float(
        string="Total Certified Percentage", compute="_compute_totals", store=True
    )
