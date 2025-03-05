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
Recommendation Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Recommendations
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Recommendation
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Recommendation Demo REST API Service",
            version="1.0",
            paths=url_for("list_recommendations", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Create a Recommendation
    This endpoint will create a Recommendation based on the data in the request body
    """
    app.logger.info("Request to Create a Recommendation...")
    check_content_type("application/json")

    recommendation = Recommendation()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    recommendation.deserialize(data)

    # Save the new Recommendation to the database
    recommendation.create()
    app.logger.info("Recommendation with new id [%s] saved!", recommendation.id)

    # Return the location of the new Recommendation
    location_url = url_for(
        "get_recommendations", recommendation_id=recommendation.id, _external=True
    )

    return (
        jsonify(recommendation.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the Recommendations"""
    app.logger.info("Request for recommendation list")

    recommendations = []

    # Parse any arguments from the query string
    product_id = request.args.get("product_id")
    customer_id = request.args.get("customer_id")
    recommend_type = request.args.get("recommend_type")
    recommend_product_id = request.args.get("recommend_product_id")

    if product_id:
        app.logger.info("Filtering by product_id: %s", product_id)
        recommendations = Recommendation.find_by_product_id(int(product_id))
    elif customer_id:
        app.logger.info("Filtering by customer_id: %s", customer_id)
        recommendations = Recommendation.find_by_customer_id(int(customer_id))
    elif recommend_type:
        app.logger.info("Filtering by recommend_type: %s", recommend_type)
        recommendations = Recommendation.find_by_recommend_type(recommend_type)
    elif recommend_product_id:
        app.logger.info("Filtering by recommend_product_id: %s", recommend_product_id)
        recommendations = Recommendation.find_by_recommend_product_id(
            int(recommend_product_id)
        )
    else:
        app.logger.info("Returning all recommendations")
        recommendations = Recommendation.all()

    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
def get_recommendations(recommendation_id):
    """
    Retrieve a single Recommendation

    This endpoint will return a Recommendation based on it's id
    """
    app.logger.info(
        "Request to Retrieve a recommendation with id [%s]", recommendation_id
    )

    # Attempt to find the Recommendation and abort if not found
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    app.logger.info("Returning recommendation: %s", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A RECOMMENDATION
######################################################################


@app.route("/recommendations/<int:recommendations_id>", methods=["PUT"])
def update_recommendations(recommendations_id):
    """
    Update a Recommendation
    This endpoint will update a Recommendation based the body that is posted
    """
    app.logger.info("Request to update recommendations with id: %d", recommendations_id)
    check_content_type("application/json")

    recommendations = Recommendation.find(recommendations_id)
    if not recommendations:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id: '{recommendations_id}' was not found.",
        )

    recommendations.deserialize(request.get_json())
    recommendations.id = recommendations_id
    recommendations.update()

    app.logger.info("Recommendation with ID: %d updated.", recommendations.id)
    return jsonify(recommendations.serialize()), status.HTTP_200_OK


    ######################################################################
    # LINK AN RECOMMENDATION ID TO A EXISTING PRODUCT
    ######################################################################
@app.route(
    "/recommendations/<int:product_id>/<int:recommendations_id>", methods=["PUT"]
)
def update_recommendations_id(product_id, recommendations_id):
    """
    Link a recommendation id to an existing product
    This endpoint will lina a recommendation id to a product.
    """
    app.logger.info("Request to update recommendations with id: %d", product_id)
    check_content_type("application/json")

    recommendations = Recommendation.find(product_id)
    if not recommendations:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id: '{product_id}' was not found.",
        )

    recommendations.deserialize(request.get_json())
    recommendations.recommendation_id = recommendations_id
    recommendations.update()

    app.logger.info("Recommendation with ID: %d updated.", recommendations.id)
    return jsonify(recommendations.serialize()), status.HTTP_200_OK


    ######################################################################
    # LINK AN RECOMMENDATION NAME TO A EXISTING PRODUCT
    ######################################################################
@app.route("/recommendations/<int:product_id>/<name>", methods=["PUT"])
def update_recommendations_name(product_id, name):
    """
    Link a recommendation name to an existing product
    This endpoint will lina a recommendation name to a product.
    """
    app.logger.info("Request to update recommendations with id: %d", product_id)
    check_content_type("application/json")

    recommendations = Recommendation.find(product_id)
    if not recommendations:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id: '{product_id}' was not found.",
        )

    recommendations.deserialize(request.get_json())
    recommendations.recommendation_name = name
    recommendations.update()

    app.logger.info("Recommendation with ID: %d updated.", recommendations.id)
    return jsonify(recommendations.serialize()), status.HTTP_200_OK


######################################################################
#  DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendations(recommendation_id):
    """
    Delete a Recommendation
    This endpoint will delete a Recommendation based the id specified in the path
    """
    app.logger.info("Request to delete recommendation with id: %d", recommendation_id)
    recommendation = Recommendation.find(recommendation_id)
    if recommendation:
        recommendation.delete()
    app.logger.info("Recommendation with ID: %d delete complete.", recommendation_id)
    return "", status.HTTP_204_NO_CONTENT
######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
