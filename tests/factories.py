"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Recommendation


class RecommendationFactory(factory.Factory):
    """Creates fake recommendations for testing"""

    class Meta:
        """Maps factory to data model"""

        model = Recommendation

    id = factory.Sequence(lambda n: n)

    product_id = factory.Sequence(
        lambda n: n + 100
    )  # Example product IDs starting at 100
    customer_id = factory.Sequence(
        lambda n: n + 200
    )  # Example customer IDs starting at 200
    recommend_type = factory.Iterator(
        ["up-sell", "cross-sell", "down-sell"]
    )  # Sample recommendation types
    recommend_product_id = factory.Sequence(
        lambda n: n + 300
    )  # Recommended product IDs
    rec_success = factory.Faker("random_int", min=0, max=100)  # Random success count
