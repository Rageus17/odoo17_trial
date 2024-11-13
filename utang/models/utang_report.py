from odoo import models, fields, api

class UtangReport(models.Model):
    _name = 'utang.report'
    _description = 'Utang Reporting'

    name = fields.Char(string='Nama', required=True)
    
    line_ids = fields.One2many('utang.line', 'utang_id', string='Report Lines')
    date_created = fields.Datetime(
        string="Create Date",
        required=True,
        help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",
        default=fields.Datetime.now)
    
    balance = fields.Float(string='Balance', compute='_compute_balance', store=True)
    total_bayar = fields.Float(string='Total Bayar', compute='_compute_totals', store=True)
    total_utang = fields.Float(string="Total Utang", compute='_compute_totals',store=True)
    status_bayar = fields.Selection([('utang','Masih ada Utang'),
         ('lunas', 'Lunas'),('lebih','Lebih Bayar')],string='Status Bayar',compute = '_compute_priority',store=True)

    @api.depends('line_ids.bayar', 'line_ids.utang')
    def _compute_totals(self):
        for report in self:
            report.total_bayar = sum(report.line_ids.mapped('bayar'))
            report.total_utang = sum(report.line_ids.mapped('utang'))

    @api.depends('total_bayar','total_utang')
    def _compute_balance(self):
        for report in self:
            report.balance = report.total_bayar - report.total_utang

    @api.depends("status_bayar","balance")
    def _compute_priority(self):
        for report in self:
            if report.balance == 0:
                report.status_bayar = 'lunas'
            elif report.balance < 0:
                report.status_bayar = 'utang'
            else:
                report.status_bayar = "lebih"
class UtangReportLines(models.Model):
    _name = 'utang.line'
    _description = "utang Report Line"
    utang_id = fields.Many2one('utang.report',string='Product')
    currency_id = fields.Many2one('res.currency', string="Currency")
    date = fields.Datetime(string="Date",required=True,default=fields.Datetime.now)
    utang = fields.Float(string='Hutang')
    bayar = fields.Float(string="Bayar")   
    # @api.depends("sale_price","cost_price")
    # def _compute_profit(self):
    #     for record in self:
    #         if record.cost_price and record.cost_price != 0:
    #             record.profit = (record.sale_price - record.cost_price)
    #         else:
    #             record.profit = 0.0  # Or any other appropriate default value

    # @api.depends("profit","quantity_sold")
    # def _compute_rev(self):
    #     for record in self:
    #         record.revenue = record.profit * record.quantity_sold