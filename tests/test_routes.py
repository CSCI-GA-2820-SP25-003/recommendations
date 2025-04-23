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

    def test_create_recommendation_with_no_content_type(self):
        """It should fail to create recommendation without Content-Type"""
        response = self.client.post(BASE_URL, data="{}", content_type=None)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertIn(
            "Content-Type must be application/json", response.get_data(as_text=True)
        )

    def test_create_recommendation_with_invalid_content_type(self):
        """It should fail to create recommendation with wrong Content-Type"""
        response = self.client.post(BASE_URL, data="{}", content_type="text/plain")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertIn(
            "Content-Type must be application/json", response.get_data(as_text=True)
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

    def test_list_recommendations_with_invalid_filter(self):
        """It should ignore unknown query filters"""
        response = self.client.get(f"{BASE_URL}?unknown=123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST UPDATE RECOMMENDATION
    # ----------------------------------------------------------
    def test_update_recommendation(self):
        """It should Update an existing Recommendation"""
        # create a recommendation to update
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the recommendation
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)

        # Modify some fields
        new_recommendation["recommend_type"] = "cross-sell"
        new_recommendation["rec_success"] = 99

        response = self.client.put(
            f"{BASE_URL}/{new_recommendation['id']}", json=new_recommendation
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the update
        updated_recommendation = response.get_json()
        self.assertEqual(updated_recommendation["recommend_type"], "cross-sell")
        self.assertEqual(updated_recommendation["rec_success"], 99)

        # Ensure the other fields remain unchanged
        self.assertEqual(
            updated_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertEqual(
            updated_recommendation["customer_id"], test_recommendation.customer_id
        )
        self.assertEqual(
            updated_recommendation["recommend_product_id"],
            test_recommendation.recommend_product_id,
        )

    def test_update_product_id_in_recommendation(self):
        """It should update the product_id for an existing Recommendation"""
        # Create a recommendation to update
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Fetch the newly created recommendation
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)

        # Update product_id (simulating a product replacement)
        new_recommendation["product_id"] = 9999

        response = self.client.put(
            f"{BASE_URL}/{new_recommendation['id']}", json=new_recommendation
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_recommendation = response.get_json()
        self.assertEqual(updated_recommendation["product_id"], 9999)

    def test_update_recommend_type(self):
        """It should update the recommend_type for an existing Recommendation"""
        # Create a recommendation to update
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Fetch the newly created recommendation
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)

        # Update the recommend_type
        new_recommendation["recommend_type"] = "up-sell"

        response = self.client.put(
            f"{BASE_URL}/{new_recommendation['id']}", json=new_recommendation
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_recommendation = response.get_json()
        self.assertEqual(updated_recommendation["recommend_type"], "up-sell")

    def test_update_recommendation_not_found(self):
        """It should return 404 when updating a non-existent recommendation"""
        response = self.client.put(f"{BASE_URL}/9999", json={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST DELETE RECOMMENDATION
    # ----------------------------------------------------------
    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recommendation_by_product_and_recommended_product(self):
        """It should delete a recommendation by product_id and recommended_product_id"""
        recommendation = RecommendationFactory()
        recommendation.create()

        response = self.client.delete(
            f"{BASE_URL}/{recommendation.product_id}/{recommendation.recommend_product_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Double check it's gone
        response = self.client.delete(
            f"{BASE_URL}/{recommendation.product_id}/{recommendation.recommend_product_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recommendation_not_found(self):
        """It should return 404 when deleting non-existent recommendation"""
        response = self.client.delete(f"{BASE_URL}/9999/8888")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
    # TEST INVALID QUERY
    # ----------------------------------------------------------
    def test_invalid_product_id_query(self):
        """It should return 400 Bad Request for an invalid product_id"""
        response = self.client.get(BASE_URL, query_string={"product_id": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertEqual(data["error"], "Invalid product_id")

    def test_invalid_customer_id_query(self):
        """It should return 400 Bad Request for an invalid customer_id"""
        response = self.client.get(BASE_URL, query_string={"customer_id": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertEqual(data["error"], "Invalid customer_id")

    def test_invalid_recommend_type_query(self):
        """It should return 400 Bad Request for an invalid recommend_type"""
        response = self.client.get(
            BASE_URL, query_string={"recommend_type": "invalid-type"}
        )  # Not in allowed list
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertEqual(
            data["error"],
            "Invalid recommend_type. Must be one of ['up-sell', 'down-sell', 'cross-sell']",
        )

    def test_invalid_recommend_product_id_query(self):
        """It should return 400 Bad Request for an invalid recommend_product_id"""
        response = self.client.get(
            BASE_URL, query_string={"recommend_product_id": "invalid"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertEqual(data["error"], "Invalid recommend_product_id")

    # ----------------------------------------------------------
    # TEST QUERY BY PRODUCT_ID
    # ----------------------------------------------------------
    def test_query_by_product_id(self):
        """It should Query Recommendations by product_id"""
        recommendations = self._create_recommendations(3)
        test_product_id = recommendations[0].product_id

        response = self.client.get(
            BASE_URL, query_string={"product_id": test_product_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(all(r["product_id"] == test_product_id for r in data))

    # ----------------------------------------------------------
    # TEST QUERY BY CUSTOMER_ID
    # ----------------------------------------------------------
    def test_query_by_customer_id(self):
        """It should Query Recommendations by customer_id"""
        recommendations = self._create_recommendations(3)
        test_customer_id = recommendations[0].customer_id

        response = self.client.get(
            BASE_URL, query_string={"customer_id": test_customer_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(all(r["customer_id"] == test_customer_id for r in data))

    # ----------------------------------------------------------
    # TEST QUERY BY RECOMMEND TYPE
    # ----------------------------------------------------------
    def test_query_by_recommend_type(self):
        """It should Query Recommendations by recommend_type"""
        recommendations = self._create_recommendations(3)
        test_recommend_type = recommendations[0].recommend_type

        response = self.client.get(
            BASE_URL, query_string={"recommend_type": test_recommend_type}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(all(r["recommend_type"] == test_recommend_type for r in data))

    # ----------------------------------------------------------
    # TEST QUERY BY RECOMMEND PRODUCT_ID
    # ----------------------------------------------------------
    def test_query_by_recommend_product_id(self):
        """It should Query Recommendations by recommend_product_id"""
        recommendations = self._create_recommendations(3)
        test_recommend_product_id = recommendations[0].recommend_product_id

        response = self.client.get(
            BASE_URL, query_string={"recommend_product_id": test_recommend_product_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(
            all(r["recommend_product_id"] == test_recommend_product_id for r in data)
        )
# ----------------------------------------------------------
    # TEST: ACTION ENDPOINT - ID NOT FOUND
    # ----------------------------------------------------------
    def test_action_customer_id_not_found(self):
        """It should return an error for a customer id that doesn't exist"""
        response = self.client.post(f"{BASE_URL}/0/action", json={"action": "suspend"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST: ACTION ENDPOINT - UNSUPPORTED ACTION
    # ----------------------------------------------------------
    def test_action_customer_invalid_action(self):
        """It should return an error for an unsupported action on a customer"""
        # Create a test customer
        test_customer = self._create_customers(1)[0]
        # Attempt an unsupported action
        response = self.client.post(
            f"{BASE_URL}/{test_customer.id}/action", json={"action": "invalid_action"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("not supported", data.get("message", ""))


    # ----------------------------------------------------------
    # TEST LINK
    # ----------------------------------------------------------
    def test_link_recommendation_product(self):
        """It should link a recommendation to a new recommended product"""
        # Create a recommendation first
        recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Fetch the created recommendation and link to a new product
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)

        new_recommend_product_id = new_recommendation["recommend_product_id"] + 999

        link_url = (
            f"{BASE_URL}/{new_recommendation['id']}/link/{new_recommend_product_id}"
        )

        response = self.client.put(link_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that recommend_product_id was updated
        updated_recommendation = response.get_json()
        self.assertEqual(
            updated_recommendation["recommend_product_id"], new_recommend_product_id
        )

    def test_link_recommendation_not_found(self):
        """It should return 404 when linking for a non-existent recommendation"""
        response = self.client.put(f"{BASE_URL}/9999/link/1234")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Add after test_link_recommendation_not_found and before test_list_with_all_filters

    # ----------------------------------------------------------
    # TEST LIKE
    # ----------------------------------------------------------

    def test_like_recommendation(self):
        """It should like a recommendation and increase its success count"""
        # Create a recommendation first
        recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Fetch the created recommendation
        new_recommendation = response.get_json()
        initial_success = new_recommendation["rec_success"]

        # Like the recommendation
        like_url = f"{BASE_URL}/{new_recommendation['id']}/like"
        response = self.client.patch(like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that rec_success was incremented
        updated_recommendation = response.get_json()
        self.assertEqual(updated_recommendation["rec_success"], initial_success + 1)

    def test_like_recommendation_not_found(self):
        """It should return 404 when liking a non-existent recommendation"""
        response = self.client.patch(f"{BASE_URL}/9999/like")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_with_all_filters(self):
        """It should handle all filters in list recommendations"""
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(
            BASE_URL,
            query_string={
                "product_id": test_recommendation.product_id,
                "customer_id": test_recommendation.customer_id,
                "recommend_type": test_recommendation.recommend_type,
                "recommend_product_id": test_recommendation.recommend_product_id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
