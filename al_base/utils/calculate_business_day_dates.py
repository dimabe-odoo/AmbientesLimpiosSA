from odoo.http import request
from datetime import timedelta
import pandas as pd

def calculate_business_day_dates(date_start, business_day):
    saturdays = pd.date_range(start=date_start, end=date_start + timedelta(days=business_day), freq='W-SAT').strftime(
        '%m/%d/%Y').tolist()
    sundays = pd.date_range(start=date_start, end=date_start + timedelta(days=business_day), freq='W-SUN').strftime(
        '%m/%d/%Y').tolist()
    holidays = request.env['custom.holidays'].search([('date', '>', date_start), ('date', '<', date_start + timedelta(days=business_day))])
    return date_start + timedelta(days=business_day + len(saturdays) + len(sundays) + len(holidays))






