from sp_api.api import Reports, Orders, Catalog
from sp_api.base import Marketplaces
from datetime import datetime, timedelta
from flask import current_app
import pandas as pd
import json

class AmazonSPAPIService:
    def __init__(self):
        self.credentials = {
            'refresh_token': current_app.config['AMAZON_REFRESH_TOKEN'],
            'lwa_app_id': current_app.config['AMAZON_CLIENT_ID'],
            'lwa_client_secret': current_app.config['AMAZON_CLIENT_SECRET'],
            'aws_access_key': current_app.config['AMAZON_AWS_ACCESS_KEY'],
            'aws_secret_key': current_app.config['AMAZON_AWS_SECRET_KEY'],
            'role_arn': current_app.config['AMAZON_ROLE_ARN'],
        }
        self.marketplace_id = current_app.config['AMAZON_MARKETPLACE_ID']
        self.reports_api = Reports(credentials=self.credentials)
        self.orders_api = Orders(credentials=self.credentials)
        self.catalog_api = Catalog(credentials=self.credentials)

    def get_sales_report(self, start_date, end_date):
        """Fetch sales report for the specified date range"""
        try:
            report_type = 'GET_FLAT_FILE_OPEN_LISTINGS_DATA'
            response = self.reports_api.create_report(
                reportType=report_type,
                dataStartTime=start_date,
                dataEndTime=end_date,
                marketplaceIds=[self.marketplace_id]
            )
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching sales report: {str(e)}")
            return None

    def get_orders_report(self, start_date, end_date):
        """Fetch orders report for the specified date range"""
        try:
            report_type = 'GET_FLAT_FILE_OPEN_LISTINGS_DATA'
            response = self.reports_api.create_report(
                reportType=report_type,
                dataStartTime=start_date,
                dataEndTime=end_date,
                marketplaceIds=[self.marketplace_id]
            )
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching orders report: {str(e)}")
            return None

    def get_inventory_report(self):
        """Fetch current inventory levels"""
        try:
            report_type = 'GET_FLAT_FILE_OPEN_LISTINGS_DATA'
            response = self.reports_api.create_report(
                reportType=report_type,
                marketplaceIds=[self.marketplace_id]
            )
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching inventory report: {str(e)}")
            return None

    def get_report_document(self, report_document_id):
        """Fetch the actual report document using the report document ID"""
        try:
            response = self.reports_api.get_report_document(report_document_id)
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching report document: {str(e)}")
            return None

    def get_product_details(self, asin):
        """Fetch product details using the Catalog API"""
        try:
            response = self.catalog_api.get_catalog_item(asin)
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching product details: {str(e)}")
            return None

    def get_recent_orders(self, days=30):
        """Fetch recent orders"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            response = self.orders_api.get_orders(
                CreatedAfter=start_date.isoformat(),
                MarketplaceIds=[self.marketplace_id]
            )
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching recent orders: {str(e)}")
            return None

    def process_sales_data(self, report_data):
        """Process sales report data into a structured format"""
        try:
            # Convert report data to DataFrame
            df = pd.DataFrame(report_data)
            
            # Group by date and calculate metrics
            daily_sales = df.groupby('date').agg({
                'quantity': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            return daily_sales.to_dict('records')
        except Exception as e:
            current_app.logger.error(f"Error processing sales data: {str(e)}")
            return None

    def get_report_status(self, report_id):
        """Check the status of a report"""
        try:
            response = self.reports_api.get_report(report_id)
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error checking report status: {str(e)}")
            return None

    def list_reports(self, report_types=None, processing_statuses=None):
        """List available reports with optional filters"""
        try:
            params = {
                'marketplaceIds': [self.marketplace_id]
            }
            if report_types:
                params['reportTypes'] = report_types
            if processing_statuses:
                params['processingStatuses'] = processing_statuses

            response = self.reports_api.get_reports(**params)
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error listing reports: {str(e)}")
            return None 