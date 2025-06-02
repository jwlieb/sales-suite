from datetime import datetime, timedelta
from app import db
from app.models import Product, KeywordPerformance
from app.services.amazon_sp_api import AmazonSPAPIService

class KeywordTracker:
    def __init__(self, sp_api_service: AmazonSPAPIService):
        self.sp_api = sp_api_service

    def track_keyword_performance(self, product: Product, keywords: list = None):
        """Track performance of keywords for a product."""
        try:
            if keywords is None:
                # Get keywords from product title and description
                keywords = self._extract_keywords(product)

            for keyword in keywords:
                # Get keyword performance data from Amazon
                performance_data = self.sp_api.get_keyword_performance(
                    product.asin,
                    keyword
                )

                # Create keyword performance record
                keyword_perf = KeywordPerformance(
                    product_id=product.id,
                    keyword=keyword,
                    search_rank=performance_data.get('rank'),
                    impressions=performance_data.get('impressions', 0),
                    clicks=performance_data.get('clicks', 0),
                    conversions=performance_data.get('conversions', 0),
                    ctr=performance_data.get('ctr', 0.0),
                    acos=performance_data.get('acos', 0.0),
                    date=datetime.utcnow().date()
                )

                db.session.add(keyword_perf)

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error tracking keyword performance: {str(e)}")
            return False

    def _extract_keywords(self, product: Product):
        """Extract keywords from product title and description."""
        # This is a simplified version. In practice, you'd want to:
        # 1. Use NLP to extract meaningful keywords
        # 2. Remove stop words
        # 3. Consider product category-specific terms
        # 4. Include variations and synonyms
        words = product.title.lower().split()
        return list(set(words))  # Remove duplicates

    def get_keyword_trends(self, product_id: int, days: int = 30):
        """Get keyword performance trends over time."""
        start_date = datetime.utcnow().date() - timedelta(days=days)
        return KeywordPerformance.query.filter(
            KeywordPerformance.product_id == product_id,
            KeywordPerformance.date >= start_date
        ).order_by(
            KeywordPerformance.date.desc(),
            KeywordPerformance.keyword
        ).all()

    def get_top_keywords(self, product_id: int, limit: int = 10):
        """Get top performing keywords for a product."""
        return KeywordPerformance.query.filter(
            KeywordPerformance.product_id == product_id,
            KeywordPerformance.date >= datetime.utcnow().date() - timedelta(days=7)
        ).order_by(
            KeywordPerformance.conversions.desc()
        ).limit(limit).all()

    def get_keyword_opportunities(self, product_id: int):
        """Identify keyword opportunities based on performance data."""
        # Get recent keyword performance
        recent_performance = KeywordPerformance.query.filter(
            KeywordPerformance.product_id == product_id,
            KeywordPerformance.date >= datetime.utcnow().date() - timedelta(days=30)
        ).all()

        opportunities = []
        for perf in recent_performance:
            # High impressions but low CTR might indicate poor listing optimization
            if perf.impressions > 1000 and perf.ctr < 0.01:
                opportunities.append({
                    'keyword': perf.keyword,
                    'type': 'low_ctr',
                    'suggestion': 'Optimize listing for better click-through rate'
                })
            
            # High clicks but low conversions might indicate pricing or content issues
            if perf.clicks > 100 and perf.conversions < 5:
                opportunities.append({
                    'keyword': perf.keyword,
                    'type': 'low_conversion',
                    'suggestion': 'Review pricing and listing content'
                })
            
            # High ACOS might indicate need for bid adjustment
            if perf.acos > 0.3:  # 30% ACOS threshold
                opportunities.append({
                    'keyword': perf.keyword,
                    'type': 'high_acos',
                    'suggestion': 'Consider adjusting bid strategy'
                })

        return opportunities

    def get_keyword_rankings(self, product_id: int):
        """Get current keyword rankings for a product."""
        return KeywordPerformance.query.filter(
            KeywordPerformance.product_id == product_id,
            KeywordPerformance.date == datetime.utcnow().date()
        ).order_by(
            KeywordPerformance.search_rank
        ).all()

    def get_keyword_health(self, product_id: int):
        """Get overall keyword health metrics."""
        recent_performance = KeywordPerformance.query.filter(
            KeywordPerformance.product_id == product_id,
            KeywordPerformance.date >= datetime.utcnow().date() - timedelta(days=30)
        ).all()

        if not recent_performance:
            return None

        return {
            'total_keywords': len(set(p.keyword for p in recent_performance)),
            'average_rank': sum(p.search_rank for p in recent_performance) / len(recent_performance),
            'total_impressions': sum(p.impressions for p in recent_performance),
            'average_ctr': sum(p.ctr for p in recent_performance) / len(recent_performance),
            'average_acos': sum(p.acos for p in recent_performance) / len(recent_performance)
        } 