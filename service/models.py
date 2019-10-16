"""
A model file that defines the data schema and database operations
"""

import logging
from mongoengine import Document, StringField, ListField, IntField, connect
from mongoengine.errors import ValidationError
from mongoengine.queryset.visitor import Q

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass
# class Product(db.Document):
#     """
#     Class that represents a product id
#     """
#     product_id = db.IntField(required=True)

class Supplier(Document):
    """
    Suppliers data schema: https://github.com/nyu-devops-fall19-suppliers/suppliers/issues/21
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    supplierName = StringField(required=True)
    address = StringField(required=False)
    productIdList = ListField(StringField(), required=False)
    averageRating = IntField(required=False)

    def __repr__(self):
        return '<Supplier %r>' % (self.supplierName)

    # def save(self):
    #     """
    #     Saves a Supplier to the data store
    #     """
    #     Supplier.logger.info('Saving %s', self.supplierName)
    #     self.save()

    # Deprecated function. Use supplier.to_json() instead
    def serialize(self):
        """ Serializes a Supplier into a dictionary """
        return {"id": str(self.id),
                "supplierName": self.supplierName,
                "address": self.address,
                "averageRating" : self.averageRating,
                "productIdList": self.productIdList}

    # Deprecated function. Use supplier = Supplier(**data) instead
    def deserialize(self, data):
        """
        Deserializes a Supplier from a dictionary
        Args:
            data (dict): A dictionary containing the Supplier data
        """
        try:
            self.supplierName = data['supplierName']
            self.address = data['address']
            self.averageRating = data['averageRating']
            # product = Product()
            self.productIdList = data['productIdList']
        except KeyError as error:
            raise DataValidationError('Invalid supplier: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid supplier: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize mongoDB from the Flask app
        connect('myDatabase')
        app.app_context().push()

    @classmethod
    def all(cls):
        """This is a function to return all suppliers"""
        cls.logger.info('Processing all suppliers')
        return cls.objects()

    @classmethod
    def find_by_name(cls, supplier_name):
        """ Find a supplier by its name """
        cls.logger.info('Processing looking for name %s', supplier_name)
        try:
            res = cls.objects.get(supplierName=supplier_name)
        except ValidationError:
            raise DataValidationError('Invalid supplier_name: failed to ' \
                                      'find a supplier with given supplier_name')
        return res


    @classmethod
    def find(cls, supplier_id):
        """Retrieves a single supplier with a given id (supplierID) """

        cls.logger.info('Getting supplier with id: %s', supplier_id)

        try:
            res = cls.objects(id=supplier_id).first()
        except ValidationError:
            return None
        return res

    @classmethod
    def find_by_product(cls, product_id):
        """Retrieves a list of supplier with a given product id """
        cls.logger.info("Getting suppliers with product id: %s", product_id)
        try:
            res = cls.objects(productIdList__in=product_id)
        except ValidationError:
            return None
        return res

    @classmethod
    def find_by_rating(cls, rating):
        """Retrieves a list of supplier with a given rating score """
        cls.logger.info("Getting suppliers with ratting score greater than: %d", rating)
        try:
            res = cls.objects(averageRating__gte=3)
        except ValidationError:
            return None
        return res

    @classmethod
    def action_make_recommendation(cls, product_id):
        """Retrieves a list of supplier with a given rating score and product id """
        cls.logger.info("Getting suppliers with ratting score greater than: %s", product_id)
        try:
            res = cls.objects(Q(productIdList__in=product_id) & Q(averageRating__gte=3))
        except ValidationError:
            return None
        return res
