from odoo import models, fields, api

class ProductMarginReport(models.Model):
    _name = 'product_margin.report'
    _description = 'Product Margin Report'
    _rec_name = 'product_name'
    
    supplier_id = fields.Many2one('res.partner', string='Vendor')
    product_name = fields.Char(string='Product', required=True)
    description = fields.Char(string="Product Description")
    #line_ids = fields.One2many('product_margin.report.line', 'report_id', string='Report Lines')

    availability = fields.Boolean(string="Availability")
    date_created = fields.Datetime(
        string="Create Date",
        required=True, copy=False,
        help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",
        default=fields.Datetime.now)
    quantity_sold = fields.Integer(string='Quantity Sold', required=True)
    currency_id = fields.Many2one('res.currency', string="Currency")
    sale_price = fields.Float(string='Sale Price', required=True, digits=(2, 3))
    cost_price = fields.Float(string='Cost Price', required=True)
    image = fields.Binary(string='Product Image')
    profit = fields.Float(string='Profit Product', compute='_compute_profit',store=True)
    margin = fields.Float(string='Margin', compute='_compute_margin',store=True,group_operator='avg')
    revenue = fields.Float(string="Gross Profit By Product",compute='_compute_rev',store=True)
    priority = fields.Selection(
        [('0', 'No Margin'),
         ('1','Low Margin'),
         ('2', 'Medium Margin'), 
         ('3', 'High Margin')], 
        string='Margin Scale',compute='_compute_margin',store=True)
    state = fields.Selection(
        [('purchase','On Purchase'),
         ('delivery', 'On Delivery'), 
         ('receive', 'Received')], 
        string='Status',required=True, readonly=True, copy=False,
   tracking=True, default='purchase')
    
    # exclude_for = fields.One2many(
    #     comodel_name='product.template.attribute.exclusion',
    #     inverse_name='product_template_attribute_value_id',
    #     string="Exclude for")
    
    def button_in_progress(self):
       self.write({
           'state': "delivery",
       })
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