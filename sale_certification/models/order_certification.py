from odoo import api, fields, models


class OrderCertification(models.Model):
    _name = "order.certification"
    _description = "Base model to define a certification"
    _order = "sequence, id"

    order_id = fields.Many2one(
        "sale.order", string="Sale Order", required=True, ondelete="cascade"
    )
    name = fields.Char(string="Certification", required=True)
    sequence = fields.Integer(string="Sequence", default=0)
    certification_line_ids = fields.One2many(
        "certification.line", "certification_id", string="Lines"
    )
    chapter_cert_ids = fields.Many2many(
        "sale.order.line", string="Certified Chapters"
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
        CertificationLine = self.env['certification.line']
        for cert in self:
            for line in cert.certification_line_ids:
                sale_line = line.sale_line_id

                if line.certify_type == "section":
                    other_chapter_lines = CertificationLine.search([
                        ('sale_line_id', '=', sale_line.id),
                        ('certification_id', 'not in', self.ids),
                        ('certify_type', '=', 'section'),
                    ], limit=1)
                    
                    if not other_chapter_lines:
                        sale_line.is_certified_chapter = False
                else:
                    other_lines = CertificationLine.search([
                        ('sale_line_id', '=', sale_line.id),
                        ('certification_id', 'not in', self.ids),
                        ('certify_type', '!=', 'section'),
                    ], limit=1)

                    if not other_lines:
                        sale_line.is_certified = False

            for chapter in cert.chapter_cert_ids:
                other_cert = self.search([
                    ('id', 'not in', cert.ids),
                    ('chapter_cert_ids', 'in', chapter.id)
                ], limit=1)

                if not other_cert:
                    chapter.is_certified_chapter = False



            
            
