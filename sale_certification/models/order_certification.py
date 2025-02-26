from odoo import api, fields, models


class OrderCertification(models.Model):
    _name = "order.certification"
    _description = "Base model to define a certification"
    _order = "sequence, id"

    order_id = fields.Many2one(
        "sale.order", string="Sale Order", required=True, ondelete="cascade"
    )
    name = fields.Char(
        string="Certification",
        required=True,
    )
    sequence = fields.Integer(string="Sequence", default=0)
    certification_line_ids = fields.One2many(
        "certification.line", "certification_id", string="Lines"
    )
    certification_date = fields.Date(string="Date", default=fields.Date.context_today)
    total_certified = fields.Float(
        string="Total Certified",
        compute="_compute_total_certified",
        store=True,
        help="Total of the certified quantities in this certification",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
    )

    @api.depends("certification_line_ids.quantity")
    def _compute_total_certified(self):
        for cert in self:
            cert.total_certified = sum(cert.certification_line_ids.mapped("quantity"))

    @api.ondelete(at_uninstall=False)
    def _unlink_and_uncertify_lines(self):
        for line in self.certification_line_ids:
            line.sale_line_id.is_certified = False
            line.sale_line_id.is_certified_chapter = False
