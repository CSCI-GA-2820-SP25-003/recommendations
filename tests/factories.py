"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Recommendation


class RecommendationFactory(factory.Factory):
    """Creates fake recommendations for testing"""

    class Meta:  # pylint: disable=R0903
        """Maps factory to data model"""

        model = Recommendation

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n + 100)
    customer_id = factory.Sequence(lambda n: n + 200)
    product_name = factory.Faker("word")
    recommendation_name = factory.Faker("word")
    recommend_type = factory.Iterator(["Up-Sell", "Cross-Sell", "Down-Sell"])
    recommend_product_id = factory.Sequence(lambda n: n + 300)
    rec_success = factory.Faker("random_int", min=0, max=100)
