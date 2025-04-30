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
from service.models import db


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
# @app.route("/")
# def index():
#     """Root URL response"""
#     app.logger.info("Request for Root URL")
#     return (
#         jsonify(
#             name="Recommendation Demo REST API Service",
#             version="1.0",
#             paths=url_for("list_recommendations", _external=True),
#         ),
#         status.HTTP_200_OK,
#     )
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################
######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route(
    "/recommendations/<int:product_id>/<int:recommend_product_id>", methods=["DELETE"]
)
def delete_recommendation(product_id, recommend_product_id):
    """
    Delete a Recommendation

    This endpoint will delete a Recommendation based on the product_id and recommend_product_id specified in the path.
    """

    app.logger.info(
        "Request to Delete a recommendation with product_id [%s] and recommend_product_id [%s]",
        product_id,
        recommend_product_id,
    )

    # Find the Recommendation in the database
    recommendation = Recommendation.query.filter_by(
        product_id=product_id, recommend_product_id=recommend_product_id
    ).first()

    # If the recommendation exists, delete it
    if recommendation:
        app.logger.info(
            "Recommendation found for product_id: %d and recommend_product_id: %d",
            product_id,
            recommend_product_id,
        )
        db.session.delete(recommendation)
        db.session.commit()
        app.logger.info(
            "Recommendation with product_id: %d and recommend_product_id: %d deleted successfully.",
            product_id,
            recommend_product_id,
        )
        return {}, status.HTTP_204_NO_CONTENT

    # If not found, return 404
    app.logger.info(
        "Recommendation with product_id: %d and recommend_product_id: %d not found.",
        product_id,
        recommend_product_id,
    )
    abort(
        status.HTTP_404_NOT_FOUND,
        f"Recommendation with product_id '{product_id}' and recommend_product_id '{recommend_product_id}' was not found.",
    )


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
def list_recommendations():  # pylint: disable=too-many-branches, too-many-return-statements
    """Returns all of the Recommendations, with optional filtering"""
    app.logger.info("Request for recommendation list with filters")

    # Retrieve query parameters
    product_id = request.args.get("product_id")
    customer_id = request.args.get("customer_id")
    recommend_type = request.args.get("recommend_type")
    recommend_product_id = request.args.get("recommend_product_id")
    product_name = request.args.get("product_name")
    recommendation_name = request.args.get("recommendation_name")
    rec_success_min = request.args.get("rec_success_min")
    rec_success_max = request.args.get("rec_success_max")

    query = Recommendation.query
    valid_recommend_types = ["Up-Sell", "Down-Sell", "Cross-Sell"]

    if product_id:
        if not product_id.isdigit():
            return jsonify(error="Invalid product_id"), status.HTTP_400_BAD_REQUEST
        query = query.filter(Recommendation.product_id == int(product_id))

    if customer_id:
        if not customer_id.isdigit():
            return jsonify(error="Invalid customer_id"), status.HTTP_400_BAD_REQUEST
        query = query.filter(Recommendation.customer_id == int(customer_id))

    if recommend_type:
        if recommend_type not in valid_recommend_types:
            return (
                jsonify(
                    error=f"Invalid recommend_type. Must be one of {valid_recommend_types}"
                ),
                status.HTTP_400_BAD_REQUEST,
            )
        query = query.filter(Recommendation.recommend_type == recommend_type)

    if recommend_product_id:
        if not recommend_product_id.isdigit():
            return (
                jsonify(error="Invalid recommend_product_id"),
                status.HTTP_400_BAD_REQUEST,
            )
        query = query.filter(
            Recommendation.recommend_product_id == int(recommend_product_id)
        )

    if product_name:
        query = query.filter(Recommendation.product_name == product_name)

    if recommendation_name:
        query = query.filter(Recommendation.recommendation_name == recommendation_name)

    if rec_success_min and rec_success_max:
        if not rec_success_min.isdigit() or not rec_success_max.isdigit():
            return (
                jsonify(error="Invalid range :()"),
                status.HTTP_400_BAD_REQUEST,
            )

        min_val = int(rec_success_min)
        max_val = int(rec_success_max)
        if min_val > max_val:
            return (
                jsonify(error="rec_success_min cannot be greater than rec_success_max"),
                status.HTTP_400_BAD_REQUEST,
            )

        query = query.filter(
            Recommendation.rec_success >= min_val, Recommendation.rec_success <= max_val
        )

    recommendations = query.all()
    results = [recommendation.serialize() for recommendation in recommendations]
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
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update_recommendations(recommendation_id):
    """
    Update a Recommendation
    This endpoint will update a Recommendation based on provided fields
    """
    app.logger.info("Request to update recommendation with id: %d", recommendation_id)
    check_content_type("application/json")

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id: '{recommendation_id}' was not found.",
        )

    data = request.get_json()
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, "No data provided for update.")

    # Update only fields that are present
    if "customer_id" in data:
        recommendation.customer_id = data["customer_id"]
    if "product_id" in data:
        recommendation.product_id = data["product_id"]
    if "product_name" in data:
        recommendation.product_name = data["product_name"]
    if "recommendation_name" in data:
        recommendation.recommendation_name = data["recommendation_name"]
    if "recommend_product_id" in data:
        recommendation.recommend_product_id = data["recommend_product_id"]
    if "recommend_type" in data:
        recommendation.recommend_type = data["recommend_type"]
    if "rec_success" in data:
        recommendation.rec_success = data["rec_success"]

    recommendation.update()

    app.logger.info("Recommendation with ID: %d updated.", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


@app.route(
    "/recommendations/<int:recommendation_id>/link/<int:recommend_product_id>",
    methods=["PUT"],
)
def link_recommendation_product(recommendation_id, recommend_product_id):
    """
    Link a recommended product to an existing recommendation
    """
    app.logger.info(
        "Request to link recommended product %d to recommendation %d",
        recommend_product_id,
        recommendation_id,
    )

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    recommendation.recommend_product_id = recommend_product_id
    recommendation.update()

    app.logger.info(
        "Recommendation %d now links to recommended product %d",
        recommendation_id,
        recommend_product_id,
    )

    return jsonify(recommendation.serialize()), status.HTTP_200_OK


@app.route("/recommendations/<int:recommendation_id>/like", methods=["PUT"])
def like_recommendation(recommendation_id):
    """Increments the success rate of a recommendation by 1"""
    app.logger.info("Request to LIKE recommendation with id [%s]", recommendation_id)

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    if recommendation.rec_success < 100:
        recommendation.rec_success += 1
        recommendation.update()

    return jsonify(recommendation.serialize()), status.HTTP_200_OK


@app.route("/recommendations/<int:recommendation_id>/dislike", methods=["PUT"])
def dislike_recommendation(recommendation_id):
    """
    Dislike a recommendation (decrement its success score by 1)
    """
    app.logger.info("Disliking recommendation with id [%s]", recommendation_id)

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    # Prevent negative values if needed
    if recommendation.rec_success > 0:
        recommendation.rec_success -= 1
        recommendation.update()

    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
#  DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendations(recommendation_id):
    """
    Delete a Recommendation
    This endpoint will delete a Recommendation based the id specified in the path
    """
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    recommendation.delete()
    return (
        jsonify(message="Recommendation deleted successfully."),
        status.HTTP_204_NO_CONTENT,
    )


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
