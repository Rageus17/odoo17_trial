from odoo import models, fields, api

class ProductMarginReport(models.Model):
    _name = 'product_margin.report'
    _description = 'Product Margin Report'
    _rec_name = 'product_name'
    
    supplier_id = fields.Many2one('res.partner', string='Vendor')
    product_name = fields.Char(string='Product', required=True)
    description = fields.Char(string="Product Description")
    image = fields.Binary()
    line_ids = fields.One2many('margin.line', 'margin_id', string='Report Lines')
    tag_ids = fields.Many2many('margin.tag',string='Tags')
    state = fields.Selection(
        [('purchase','On Purchase'),
         ('delivery', 'On Delivery'), 
         ('receive', 'Received')], 
        string='Status',required=True, index=True,tracking=True, default='purchase')
    date_created = fields.Datetime(
        string="Create Date",
        required=True, copy=False,
        help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",
        default=fields.Datetime.now)
    availability = fields.Boolean(string="Availability")
    total_revenue = fields.Float(string='Total Revenue', compute='_compute_totals', store=True)
    total_sold = fields.Float(string='Total Quantity Sold', compute='_compute_totals', store=True)
    total_cost = fields.Float(string="Total Cost", compute='_compute_margin',store=True)
    average_margin = fields.Float(string="Average Margin",compute='_compute_margin', store=True)
    priority = fields.Selection(
        [('0', 'No Margin'),
         ('1','Low Margin'),
         ('2', 'Medium Margin'), 
         ('3', 'High Margin')], 
        string='Margin Scale',compute='_compute_priority',store=True)

    @api.depends('line_ids.revenue', 'line_ids.quantity_sold')
    def _compute_totals(self):
        for report in self:
            report.total_revenue = sum(report.line_ids.mapped('revenue'))
            report.total_sold = sum(report.line_ids.mapped('quantity_sold'))

    @api.depends('line_ids.cost_price')
    def _compute_margin(self):
        for report in self:
            report.total_cost = sum(line.cost_price * line.quantity_sold for line in report.line_ids)
            if report.total_cost == 0:
                report.average_margin = 0
            else:
                report.average_margin = report.total_revenue / report.total_cost

    @api.depends("priority","average_margin")
    def _compute_priority(self):
        for report in self:
            if report.average_margin < 0.2:
                report.priority = '1'
            elif 0.2<= report.average_margin <0.5:
                report.priority = '2'
            elif report.average_margin>=0.5:  # High margin
                    report.priority = '3'
            else:
                report.priority="0"

    def button_in_progress(self):
       self.write({
           'state': "delivery",
       })
    def action_set_purchase(self):
        self.write({'state': 'purchase'})
    def action_set_delivery(self):
        self.write({'state': 'delivery'})
    def action_set_receive(self):
        self.write({'state': 'receive'})

class ProductMarginReportLines(models.Model):
    _name = 'margin.line'
    _description = "Margin Report Line"
    margin_id = fields.Many2one('product_margin.report',string='Product')
    date = fields.Datetime(string="Date",required=True,default=fields.Datetime.now)
    quantity_sold = fields.Integer(string='Quantity Sold', required=True)
    currency_id = fields.Many2one('res.currency', string="Currency")
    sale_price = fields.Float(string='Sale Price', required=True, digits=(2, 3))
    cost_price = fields.Float(string='Cost Price', required=True)
    profit = fields.Float(string='Profit Product', compute='_compute_profit',store=True)
    margin = fields.Float(string='Margin', compute='_compute_margin',store=True,group_operator='avg')
    revenue = fields.Float(string="Gross Profit By Product",compute='_compute_rev',store=True)
    priority = fields.Selection(
        [('0', 'No Margin'),
         ('1','Low Margin'),
         ('2', 'Medium Margin'), 
         ('3', 'High Margin')], 
        string='Margin Scale',compute='_compute_margin',store=True)

    @api.depends("sale_price", "cost_price")
    def _compute_margin(self):
        for record in self:
            if record.cost_price != 0:
                record.margin = (record.sale_price - record.cost_price) / record.cost_price
                if record.margin < 0.2:  # Low margin
                    record.priority = '1'
                elif record.margin <0:
                    record.priority='0'
                elif 0.2 <= record.margin < 0.5:  # Medium margin
                    record.priority = '2'
                elif record.margin>=0.5:  # High margin
                    record.priority = '3'
            else:
                record.margin = 0
                record.priority = '0'  # Default to Low if no cost price


   
    @api.depends("sale_price","cost_price")
    def _compute_profit(self):
        for record in self:
            if record.cost_price and record.cost_price != 0:
                record.profit = (record.sale_price - record.cost_price)
            else:
                record.profit = 0.0  # Or any other appropriate default value

    @api.depends("profit","quantity_sold")
    def _compute_rev(self):
        for record in self:
            record.revenue = record.profit * record.quantity_sold