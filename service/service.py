"""
Paths:
------
GET /suppliers - Returns a list all of the suppliers
GET /suppliers/{id} - Returns the supplier with a given id number
POST /suppliers - creates a new supplier record in the database
PUT /suppliers/{id} - updates a supplier record in the database
DELETE /suppliers/{id} - deletes a supplier record in the database
GET /suppliers?averageRating={averageRating} - queries a list of suppliers with given average rating
ACTION /suppliers/{product_id}/recommend - recommends all suppliers that sells given product and has high ratings
"""

import sys
import uuid
import logging
from functools import wraps
import json
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse, inputs, apidoc
from werkzeug.exceptions import NotFound
from service.models import Supplier, DataValidationError

from . import app

# server = Flask(__name__)
# server.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"

# MongoEngine connects to the MongoDB server running on port 27017 on localhost,
# to the database named myDatabase.
# This database is exposed as the db attribute. (mongo.db)

# Document the type of autorization required
# authorizations = {
#     'apikey': {
#         'type': 'apiKey',
#         'in': 'header',
#         'name': 'X-API-KEY'
#     }
# }

@app.route('/')
def index():
    """ Index Page """
    return app.send_static_file("index.html")

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Supplier Demo REST API Service',
          description='This is a sample server Supplier server.',
          default='Suppliers',
          default_label='Suppliers operations',
          doc='/'
        # default also could use doc='/apidocs/'
        #   authorizations=authorizations,
        #   prefix='/suppliers'
         )

# Define the model so that the docs reflect what can be sent
id_fields = {}
id_fields['$oid'] = fields.String(readOnly=True)
supplier_model = api.model('Supplier', {
    '_id': fields.Nested(id_fields, title = '_id',
                         description='The unique id assigned internally by service'),
    'supplierName': fields.String(required=True,
                          description='The name of the Supplier'),
    'address': fields.String(required=False,
                              description='The address of the Supplier'),
    'productIdList': fields.List(fields.String, required=False,
                                description='The product list of the Supplier'),
    'averageRating': fields.Integer(required = False,
                                description='The average rating of the Supplier')
})
# supplier_model = api.schema_model('Supplier', {
#     '_id' : {'$oid' : {'type' : 'string'}},
#     'address': {'type' : 'string'},
#     'productIdList' : {}

# })

create_model = api.model('Supplier', {
    'supplierName': fields.String(required=True,
                          description='The name of the Supplier'),
    'address': fields.String(required=False,
                              description='The address of the Supplier'),
    'productIdList': fields.List(fields.String, required=False,
                                description='The product list of the Supplier'),
    'averageRating' : fields.Integer(required = False,
                                description='The average rating of the Supplier')
})

# query string arguments
# supplier_args = reqparse.RequestParser()
# supplier_args.add_argument('supplierName', type=str, required=False, help='List Suppliers by name')
# supplier_args.add_argument('address', type=str, required=False, help='List Suppliers by address')
# supplier_args.add_argument('averageRating', type=int, required=False, help='List Suppliers by rating score')
# supplier_args.add_argument('rating', type=int, required=False, help='List Suppliers by rating score')

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

######################################################################
# Authorization Decorator
######################################################################
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'X-API-KEY' in request.headers:
#             token = request.headers['X-API-KEY']

#         if app.config.get('API_KEY') and app.config['API_KEY'] == token:
#             return f(*args, **kwargs)
#         else:
#             return {'message': 'Invalid or missing token'}, 401

#     return decorated

######################################################################
# Function to generate a random API key (good for testing)
######################################################################
# def generate_apikey():
#     """ Helper function used when testing API keys """
#     return uuid.uuid4().hex

######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)

@app.route('/apidocs/')
def apidoc_page():
    """API Documentation Page"""
    return apidoc.ui_for(api)

######################################################################
#  PATH: /suppliers/{id}
######################################################################
@api.route('/suppliers/<supplier_id>')
@api.param('supplier_id', 'The Supplier Identifier')
class SupplierResource(Resource):
    """
    SupplierResource class

    Allows the manipulation of a single Supplier
    GET /suppliers/{id} - Returns a Supplier with the id
    PUT /suppliers/{id} - Update a Supplier with the id
    DELETE /suppliers/{id} -  Deletes a Supplier with the id
    """
    #------------------------------------------------------------------
    # RETRIEVE A SUPPLIER
    #------------------------------------------------------------------ 

    @api.doc('get_suppliers')
    @api.response(404, 'Supplier Not Found')
    @api.marshal_with(supplier_model)
    def get(self, supplier_id):
        """
        Retrieve a single Supplier

        This endpoint will return a Supplier based on it's id
        """ 
        app.logger.info("Request to Retrieve a Supplier with id [%s]", supplier_id)   
        supplier = Supplier.find(supplier_id)
        if not supplier:
            api.abort(status.HTTP_404_NOT_FOUND, "Supplier with id '{}' was not found.".format(supplier_id))   
        return json.loads(supplier.to_json()), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING SUPPLIER
    #------------------------------------------------------------------
    @api.doc('update_a_supplier')
    @api.response(404, 'Supplier not found')
    @api.response(400, 'The posted supplier data was not valid')
    @api.expect(supplier_model)
    @api.marshal_with(supplier_model)
    # @token_required
    def put(self, supplier_id):
        """ Update a supplier """
        app.logger.info('Request to update a supplier with id [%s]', supplier_id)
        check_content_type('application/json')
        supplier = Supplier.find(supplier_id)
        data = request.get_json()
        if not supplier:
            return api.abort(status.HTTP_404_NOT_FOUND, "Supplier with id '{}' not found".format(supplier_id))
        supplier.update(**data)
        # supplier.reload()
        supplier = Supplier.find(supplier.id)
        return json.loads(supplier.to_json()), status.HTTP_200_OK
    
    #------------------------------------------------------------------
    # DELETE A SUPPLIER
    #------------------------------------------------------------------

    @api.doc('delete_suppliers')
    @api.response(204, 'Supplier deleted')
    # @token_required
    def delete(self, supplier_id):
        """
        Delete a Supplier

        This endpoint will delete a Supplier based the id specified in the path
        """
        app.logger.info('Request to Delete a supplier with id [%s]', supplier_id)
        supplier = Supplier.find(supplier_id)
        if supplier:
            supplier.delete()
        
        return '', status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /suppliers
######################################################################
@api.route('/suppliers', strict_slashes = True)
class SupplierCollection(Resource):
    """ Handles all interactions with collections of Suppliers """
    #------------------------------------------------------------------
    # LIST ALL SUPPLIERS
    #------------------------------------------------------------------
    @api.doc('list_suppliers')
    # @api.expect(supplier_args, validate=False)
    @api.marshal_list_with(supplier_model)
    @api.response(400, 'Bad Request')
    def get(self):
        """ Returns all of the Suppliers """
        app.logger.info('Request to list Suppliers...')
        suppliers = []
        # args = supplier_args.parse_args()
        rating = request.args.get('rating')
        averageRating = request.args.get('averageRating')
        if rating:
            app.logger.info('Filtering by rating: %s', rating)
            suppliers = Supplier.find_by_rating(rating)
            if len(suppliers) == 0:
                return '', status.HTTP_400_BAD_REQUEST
        elif averageRating:
            app.logger.info('Filtering by rating: %s', averageRating)
            suppliers = Supplier.find_by_equals_to_rating(averageRating)
            if len(suppliers) == 0:
                return '', status.HTTP_400_BAD_REQUEST
        else:
            suppliers = Supplier.all()

        app.logger.info('[%s] suppliers returned', len(suppliers))
        results = [json.loads(supplier.to_json()) for supplier in suppliers]
        return results, status.HTTP_200_OK
    
    #------------------------------------------------------------------
    # ADD A NEW SUPPLIER
    #------------------------------------------------------------------
    @api.doc('create_suppliers')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Supplier created successfully')
    @api.marshal_with(supplier_model, code=201)
    # @token_required
    def post(self):
        """
        Creates a supplier
        This endpoint will create a supplier based the data in the body that is posted
        """
        app.logger.info('Request to Create a supplier')
        check_content_type('application/json')
        data = request.get_json()
        if not isinstance(data,dict):
            data = json.loads(data)
        try:
            data['supplierName']
        except KeyError as error:
            raise DataValidationError('Invalid supplier: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid supplier: body of request contained'
                                    'bad or no data')
        supplier = Supplier(**data)
        supplier.save()
        app.logger.debug('Payload = %s', api.payload)
        app.logger.info('supplier with new id [%s] saved!', supplier.id)
        location_url = api.url_for(SupplierResource, supplier_id=supplier.id, _external=True)
        return json.loads(supplier.to_json()), status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
#  PATH: /suppliers/{product_id}/recommend
######################################################################
@api.route('/suppliers/<productId>/recommend')
@api.param('productId', 'The product identifier')
class ProductResource(Resource):
    @api.doc('recommend_suppliers')
    @api.response(404, 'Supplier not found')
    def get(self, productId):
        """ Recommend a supplier given a product id"""
        app.logger.info('Recommend suppliers')
        suppliers = Supplier.action_make_recommendation(productId)
        if len(suppliers) <= 0:
            return api.abort(status.HTTP_404_NOT_FOUND, 'Supplier Not Found')
        app.logger.info('[%s] suppliers returned', len(suppliers))
        results = [json.loads(supplier.to_json()) for supplier in suppliers]
        return results, status.HTTP_200_OK

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the mongoengine """
    global app
    Supplier.init_db(app)

def check_content_type(content_type):
    """ Checks whether the request content type is correct """
    
    if request.headers['Content-Type'] != content_type:
        app.logger.error(
            'Invalid Content-Type: %s',
            request.headers['Content-Type'])
        abort(415, 'Content-Type must be {}'.format(content_type))
