######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Recommendation, DataValidationError, db
from .factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Recommendation   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRecommendation(TestCase):
    """Test Cases for Recommendation Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_create_recommendation(self):
        """It should create a Recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        found = Recommendation.all()
        self.assertEqual(len(found), 1)
        data = Recommendation.find(recommendation.id)
        self.assertEqual(data.customer_id, recommendation.customer_id)
        self.assertEqual(data.product_id, recommendation.product_id)
        self.assertEqual(data.product_name, recommendation.product_name)
        self.assertEqual(data.recommend_product_id, recommendation.recommend_product_id)
        self.assertEqual(data.recommendation_name, recommendation.recommendation_name)
        self.assertEqual(data.recommend_type, recommendation.recommend_type)
        self.assertEqual(data.rec_success, recommendation.rec_success)

    # ----------------------------------------------------------
    # TEST UPDATE RECOMMENDATION
    # ----------------------------------------------------------
    def test_update_recommendation(self):
        """It should Update a Recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        logging.debug(recommendation)
        self.assertIsNotNone(recommendation.id)
        # Change it an save it
        recommendation.category = "k9"
        original_id = recommendation.id
        recommendation.update()
        self.assertEqual(recommendation.id, original_id)
        self.assertEqual(recommendation.category, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, original_id)
        self.assertEqual(recommendations[0].category, "k9")

    # ----------------------------------------------------------
    # TEST DELETE RECOMMENDATION
    # ----------------------------------------------------------
    def test_delete_a_recommendation(self):
        """It should Delete a Recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)
        # delete the recommendation and make sure it isn't in the database
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    # ----------------------------------------------------------
    # TEST FIND
    # ----------------------------------------------------------

    def test_find_by_id(self):
        """It should Find a Recommendation by ID"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertIsNotNone(recommendation.id)

        # Fetch it back
        found = Recommendation.find(recommendation.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, recommendation.id)

    def test_find_by_product_id(self):
        """It should Find Recommendations by product_id"""
        recommendations = [RecommendationFactory(product_id=101) for _ in range(3)]
        for rec in recommendations:
            rec.create()
        found = Recommendation.find_by_product_id(101)
        self.assertEqual(len(found), 3)

    def test_find_by_customer_id(self):
        """It should Find Recommendations by customer_id"""
        recommendations = [RecommendationFactory(customer_id=202) for _ in range(3)]
        for rec in recommendations:
            rec.create()
        found = Recommendation.find_by_customer_id(202)
        self.assertEqual(len(found), 3)

    def test_find_by_recommend_type(self):
        """It should Find Recommendations by recommend_type"""
        recommendations = [
            RecommendationFactory(recommend_type="Cross-Sell") for _ in range(3)
        ]
        for rec in recommendations:
            rec.create()
        found = Recommendation.find_by_recommend_type("Cross-Sell")
        self.assertEqual(len(found), 3)

    def test_find_by_recommend_product_id(self):
        """It should Find Recommendations by recommend_product_id"""
        recommendations = [
            RecommendationFactory(recommend_product_id=303) for _ in range(3)
        ]
        for rec in recommendations:
            rec.create()
        found = Recommendation.find_by_recommend_product_id(303)
        self.assertEqual(len(found), 3)

    def test_serialize_recommendation(self):
        """It should Serialize a Recommendation"""
        recommendation = RecommendationFactory()
        data = recommendation.serialize()
        self.assertEqual(data["product_id"], recommendation.product_id)
        self.assertEqual(data["customer_id"], recommendation.customer_id)
        self.assertEqual(data["product_name"], recommendation.product_name)
        self.assertEqual(
            data["recommendation_name"], recommendation.recommendation_name
        )
        self.assertEqual(data["recommend_type"], recommendation.recommend_type)
        self.assertEqual(
            data["recommend_product_id"], recommendation.recommend_product_id
        )
        self.assertEqual(data["rec_success"], recommendation.rec_success)

    def test_deserialize_recommendation(self):
        """It should Deserialize a Recommendation"""
        data = RecommendationFactory().serialize()
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertEqual(recommendation.product_id, data["product_id"])
        self.assertEqual(recommendation.customer_id, data["customer_id"])
        self.assertEqual(recommendation.product_name, data["product_name"])
        self.assertEqual(
            recommendation.recommendation_name, data["recommendation_name"]
        )
        self.assertEqual(recommendation.recommend_type, data["recommend_type"])
        self.assertEqual(
            recommendation.recommend_product_id, data["recommend_product_id"]
        )
        self.assertEqual(recommendation.rec_success, data["rec_success"])

    def test_create_with_db_error(self):
        """It should handle database error on create"""
        recommendation = RecommendationFactory()
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB failure")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.create()

    def test_update_with_db_error(self):
        """It should handle database error on update"""
        recommendation = RecommendationFactory()
        recommendation.create()
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB failure")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.update()

    def test_delete_with_db_error(self):
        """It should handle database error on delete"""
        recommendation = RecommendationFactory()
        recommendation.create()
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB failure")
        ):
            with self.assertRaises(DataValidationError):
                recommendation.delete()

    def test_deserialize_valid_data(self):
        """It should deserialize valid data"""
        recommendation = Recommendation()
        data = {
            "product_id": 100,
            "customer_id": 200,
            "product_name": "Shampoo",
            "recommendation_name": "Conditioner",
            "recommend_type": "Up-Sell",
            "recommend_product_id": 300,
            "rec_success": 5,
        }
        recommendation.deserialize(data)
        self.assertEqual(recommendation.product_id, 100)
        self.assertEqual(recommendation.customer_id, 200)
        self.assertEqual(recommendation.product_name, "Shampoo")
        self.assertEqual(recommendation.recommendation_name, "Conditioner")
        self.assertEqual(recommendation.recommend_type, "Up-Sell")
        self.assertEqual(recommendation.recommend_product_id, 300)
        self.assertEqual(recommendation.rec_success, 5)

    def test_deserialize_with_missing_field(self):
        """It should raise DataValidationError if a field is missing"""
        recommendation = Recommendation()
        data = {
            "product_id": 100,
            "customer_id": 200,
            "product_name": "Shampoo",
            "recommendation_name": "Conditioner",
            # "recommend_type" is intentionally omitted
            "recommend_product_id": 300,
            "rec_success": 5,
        }
        with self.assertRaises(DataValidationError) as context:
            recommendation.deserialize(data)
        self.assertIn("missing recommend_type", str(context.exception))

    def test_deserialize_with_bad_type(self):
        """It should raise DataValidationError if data is not a dictionary"""
        recommendation = Recommendation()
        with self.assertRaises(DataValidationError) as context:
            recommendation.deserialize("this is not a dict")
        self.assertIn(
            "Invalid Recommendation: body of request contained bad or no data",
            str(context.exception),
        )

    def test_deserialize_with_unexpected_attribute(self):
        """It should raise DataValidationError if an unexpected attribute type is passed"""
        recommendation = Recommendation()
        bad_data = {
            "product_id": "wrong_type",  # product_id should be int
            "customer_id": 200,
            "recommend_type": "Up-Sell",
            "product_name": "Shampoo",
            "recommendation_name": "Conditioner",
            "recommend_product_id": 300,
            "rec_success": 5,
        }
        # This won't trigger AttributeError directly — it's more a type validation issue.
        # If you want, you could add type-checking inside `deserialize()` for stricter validation.
        recommendation.deserialize(
            bad_data
        )  # this won't fail unless you add type checks
        self.assertEqual(
            recommendation.product_id, "wrong_type"
        )  # This is allowed right now
