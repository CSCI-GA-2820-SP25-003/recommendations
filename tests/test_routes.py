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
from urllib.parse import quote_plus
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
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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
        self.assertEqual(new_recommendation["name"], test_recommendation.name)
        self.assertEqual(new_recommendation["address"], test_recommendation.address)
        self.assertEqual(new_recommendation["email"], test_recommendation.email)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_recommendation = response.get_json()
        self.assertEqual(new_recommendation["name"], test_recommendation.name)
        self.assertEqual(new_recommendation["address"], test_recommendation.address)
        self.assertEqual(new_recommendation["email"], test_recommendation.email)

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
        self.assertEqual(found_recommendation.name, recommendation.name)
        self.assertEqual(found_recommendation.address, recommendation.address)
        self.assertEqual(found_recommendation.email, recommendation.email)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------
    def test_query_by_name(self):
        """It should Query Recommendations by name"""
        recommendations = self._create_recommendations(5)
        test_name = recommendations[0].name
        name_count = len(
            [
                recommendation
                for recommendation in recommendations
                if recommendation.name == test_name
            ]
        )
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["name"], test_name)

    def test_query_recommendation_list_by_address(self):
        """It should Query Recommendations by Address"""
        recommendations = self._create_recommendations(10)
        test_address = recommendations[0].address
        address_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.address == test_address
        ]
        response = self.client.get(
            BASE_URL, query_string=f"address={quote_plus(test_address)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(address_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["address"], test_address)

    def test_query_recommendation_list_by_email(self):
        """It should Query Recommendations by Email"""
        recommendations = self._create_recommendations(10)
        test_email = recommendations[0].email
        email_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.email == test_email
        ]
        response = self.client.get(
            BASE_URL, query_string=f"email={quote_plus(test_email)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(email_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["email"], test_email)
