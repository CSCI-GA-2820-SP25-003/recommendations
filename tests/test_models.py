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
        self.assertEqual(data.product_id, recommendation.product_id)
        self.assertEqual(data.customer_id, recommendation.customer_id)
        self.assertEqual(data.recommend_type, recommendation.recommend_type)
        self.assertEqual(data.recommend_product_id, recommendation.recommend_product_id)
        self.assertEqual(data.rec_success, recommendation.rec_success)

    # Todo: Add your test cases here...
    
    # ----------------------------------------------------------
    # TEST UPDATE RECOMMENDATION
    # ----------------------------------------------------------
    def test_update_a_recommendation(self):
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

    # def test_update_no_id(self):
    #     """It should not Update a Recommendation with no id"""
    #     recommendation = RecommendationFactory()
    #     logging.debug(recommendation)
    #     recommendation.id = None
    #     self.assertRaises(DataValidationError, recommendation.update)




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
