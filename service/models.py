"""
Models for Recommendation

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()  


class DataValidationError(Exception):
    """Used for any data validation errors when deserializing"""


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    Table Schema
    id ->                   the recommendation id
    product_id ->           product id
    customer_id ->          customer id
    recommend_type ->       "up-sell", "cross-sell", "down-sell"
    recommend_product_id->  id of the recommended product
    rec_success ->          recommendation success rate
    """
    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    recommend_type = db.Column(db.String(63), nullable=False)
    recommend_product_id = db.Column(db.Integer, nullable=False)
    rec_success = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Recommendation product_id={self.product_id},\
                recommend_product_id={self.recommend_product_id} id=[{self.id}]>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        logger.info("Creating recommendation for product_id =%s", self.product_id)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving %s", self.id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Recommendation from the data store"""
        logger.info("Deleting %s", self.id)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "customer_id": self.customer_id,
            "recommend_type": self.recommend_type,
            "recommend_product_id": self.recommend_product_id,
            "rec_success": self.rec_success,
        }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.customer_id = data["customer_id"]
            self.recommend_type = data["recommend_type"]
            self.recommend_product_id = data["recommend_product_id"]
            self.rec_success = data["rec_success"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Recommendations in the database"""
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """
        Finds a Recommendation by its ID

        :param by_id: the id of the Recommendation to retrieve
        :type by_id: int

        :return: the Recommendation with the given id or None if not found
        :rtype: Recommendation
        """
        logger.info("Processing lookup for recommendation id=%s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_product_id(cls, product_id: int) -> list:
        """
        Finds all Recommendations for a given product_id

        :param product_id: the product_id to search for
        :type product_id: int

        :return: a list of Recommendations for that product
        :rtype: list
        """
        logger.info("Processing product_id query for %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id).all()

    @classmethod
    def find_by_customer_id(cls, customer_id: int) -> list:
        """
        Finds all Recommendations for a given customer_id

        :param customer_id: the customer_id to search for
        :type customer_id: int

        :return: a list of Recommendations for that customer
        :rtype: list
        """
        logger.info("Processing customer_id query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id).all()

    @classmethod
    def find_by_recommend_type(cls, recommend_type: str) -> list:
        """
        Finds all Recommendations of a given type (e.g., up-sell, cross-sell)

        :param recommend_type: the type of recommendation to search for
        :type recommend_type: str

        :return: a list of Recommendations with that type
        :rtype: list
        """
        logger.info("Processing recommend_type query for %s ...", recommend_type)
        return cls.query.filter(cls.recommend_type == recommend_type).all()

    @classmethod
    def find_by_recommend_product_id(cls, recommend_product_id: int) -> list:
        """
        Finds all Recommendations that recommend a specific product

        :param recommend_product_id: the product_id being recommended
        :type recommend_product_id: int

        :return: a list of Recommendations that recommend this product
        :rtype: list
        """
        logger.info(
            "Processing recommend_product_id query for %s ...", recommend_product_id
        )
        return cls.query.filter(cls.recommend_product_id == recommend_product_id).all()
