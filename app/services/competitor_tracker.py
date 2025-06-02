from datetime import datetime, timedelta
from app import db
from app.models import Product, CompetitorPrice
from app.services.amazon_sp_api import AmazonSPAPIService

class CompetitorTracker:
    def __init__(self, sp_api_service: AmazonSPAPIService):
        self.sp_api = sp_api_service

    def track_competitor_prices(self, product: Product):
        """Track prices of competing products for a given ASIN."""
        try:
            # Get competing products from Amazon's API
            competitors = self.sp_api.get_competing_offers(product.asin)
            
            for competitor in competitors:
                price = CompetitorPrice(
                    product_id=product.id,
                    competitor_asin=competitor['asin'],
                    price=competitor['price'],
                    shipping_price=competitor.get('shipping_price', 0.0),
                    is_prime=competitor.get('is_prime', False),
                    is_fba=competitor.get('is_fba', False),
                    condition=competitor.get('condition', 'New')
                )
                db.session.add(price)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error tracking competitor prices: {str(e)}")
            return False

    def get_price_history(self, product_id: int, days: int = 30):
        """Get price history for a product's competitors."""
        start_date = datetime.utcnow() - timedelta(days=days)
        return CompetitorPrice.query.filter(
            CompetitorPrice.product_id == product_id,
            CompetitorPrice.timestamp >= start_date
        ).order_by(CompetitorPrice.timestamp).all()

    def get_price_alerts(self, product_id: int, threshold: float = 0.1):
        """Get alerts for significant price changes."""
        # Get the latest prices
        latest_prices = db.session.query(
            CompetitorPrice.competitor_asin,
            CompetitorPrice.price
        ).filter(
            CompetitorPrice.product_id == product_id
        ).order_by(
            CompetitorPrice.timestamp.desc()
        ).all()

        # Get previous prices
        previous_prices = db.session.query(
            CompetitorPrice.competitor_asin,
            CompetitorPrice.price
        ).filter(
            CompetitorPrice.product_id == product_id,
            CompetitorPrice.timestamp < datetime.utcnow() - timedelta(hours=24)
        ).order_by(
            CompetitorPrice.timestamp.desc()
        ).all()

        alerts = []
        for latest, previous in zip(latest_prices, previous_prices):
            if latest[0] == previous[0]:  # Same competitor
                price_change = (latest[1] - previous[1]) / previous[1]
                if abs(price_change) >= threshold:
                    alerts.append({
                        'competitor_asin': latest[0],
                        'price_change': price_change,
                        'old_price': previous[1],
                        'new_price': latest[1]
                    })

        return alerts

    def get_market_position(self, product_id: int):
        """Analyze product's position in the market based on competitor prices."""
        latest_prices = CompetitorPrice.query.filter(
            CompetitorPrice.product_id == product_id,
            CompetitorPrice.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).all()

        if not latest_prices:
            return None

        prices = [p.price for p in latest_prices]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        return {
            'average_market_price': avg_price,
            'lowest_price': min_price,
            'highest_price': max_price,
            'price_range': max_price - min_price,
            'competitor_count': len(prices)
        } 