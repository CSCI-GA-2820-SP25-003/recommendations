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
TestRecommendation API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Recommendation
from .factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRecommendationService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create recommendations
    ############################################################
    def _create_recommendations(self, count: int = 1) -> list:
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test recommendation",
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Recommendation Demo REST API Service")

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        test_recommendation = RecommendationFactory()
        logging.debug("Test Recommendation: %s", test_recommendation.serialize())
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_recommendation = response.get_json()
        self.assertEqual(
            new_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertEqual(
            new_recommendation["customer_id"], test_recommendation.customer_id
        )
        self.assertEqual(
            new_recommendation["recommend_type"], test_recommendation.recommend_type
        )
        self.assertEqual(
            new_recommendation["recommend_product_id"],
            test_recommendation.recommend_product_id,
        )
        self.assertEqual(
            new_recommendation["rec_success"], test_recommendation.rec_success
        )

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_recommendation = response.get_json()
        self.assertEqual(
            new_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertEqual(
            new_recommendation["customer_id"], test_recommendation.customer_id
        )
        self.assertEqual(
            new_recommendation["recommend_type"], test_recommendation.recommend_type
        )
        self.assertEqual(
            new_recommendation["recommend_product_id"],
            test_recommendation.recommend_product_id,
        )
        self.assertEqual(
            new_recommendation["rec_success"], test_recommendation.rec_success
        )

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_list_all_recommendations(self):
        """It should List all Recommendations in the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        # Create 5 Recommendations
        for _ in range(5):
            recommendation = RecommendationFactory()
            recommendation.create()
        # See if we get back 5 recommendations
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 5)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_read_a_recommendation(self):
        """It should Read a Recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        # Fetch it back
        found_recommendation = Recommendation.find(recommendation.id)
        self.assertEqual(found_recommendation.id, recommendation.id)
        self.assertEqual(found_recommendation.product_id, recommendation.product_id)
        self.assertEqual(found_recommendation.customer_id, recommendation.customer_id)
        self.assertEqual(
            found_recommendation.recommend_type, recommendation.recommend_type
        )
        self.assertEqual(
            found_recommendation.recommend_product_id,
            recommendation.recommend_product_id,
        )
        self.assertEqual(found_recommendation.rec_success, recommendation.rec_success)

    # ----------------------------------------------------------
    # TEST QUERY BY PRODUCT_ID
    # ----------------------------------------------------------
    def test_query_by_product_id(self):
        """It should Query Recommendations by product_id"""
        recommendations = self._create_recommendations(5)
        test_product_id = recommendations[0].product_id
        product_id_count = len(
            [r for r in recommendations if r.product_id == test_product_id]
        )

        response = self.client.get(
            BASE_URL, query_string=f"product_id={test_product_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), product_id_count)

        for recommendation in data:
            self.assertEqual(recommendation["product_id"], test_product_id)

    # ----------------------------------------------------------
    # TEST QUERY BY CUSTOMER_ID
    # ----------------------------------------------------------
    def test_query_by_customer_id(self):
        """It should Query Recommendations by customer_id"""
        recommendations = self._create_recommendations(10)
        test_customer_id = recommendations[0].customer_id
        customer_id_recommendations = [
            r for r in recommendations if r.customer_id == test_customer_id
        ]

        response = self.client.get(
            BASE_URL, query_string=f"customer_id={test_customer_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(customer_id_recommendations))

        for recommendation in data:
            self.assertEqual(recommendation["customer_id"], test_customer_id)

    # ----------------------------------------------------------
    # TEST QUERY BY RECOMMEND TYPE
    # ----------------------------------------------------------
    def test_query_by_recommend_type(self):
        """It should Query Recommendations by recommend_type"""
        recommendations = self._create_recommendations(10)
        test_recommend_type = recommendations[0].recommend_type
        type_recommendations = [
            r for r in recommendations if r.recommend_type == test_recommend_type
        ]

        response = self.client.get(
            BASE_URL, query_string=f"recommend_type={test_recommend_type}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(type_recommendations))

        for recommendation in data:
            self.assertEqual(recommendation["recommend_type"], test_recommend_type)

    # ----------------------------------------------------------
    # TEST QUERY BY RECOMMEND PRODUCT_ID
    # ----------------------------------------------------------
    def test_query_by_recommend_product_id(self):
        """It should Query Recommendations by recommend_product_id"""
        recommendations = self._create_recommendations(10)
        test_recommend_product_id = recommendations[0].recommend_product_id
        recommend_product_recommendations = [
            r
            for r in recommendations
            if r.recommend_product_id == test_recommend_product_id
        ]

        response = self.client.get(
            BASE_URL, query_string=f"recommend_product_id={test_recommend_product_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(recommend_product_recommendations))

        for recommendation in data:
            self.assertEqual(
                recommendation["recommend_product_id"], test_recommend_product_id
            )
