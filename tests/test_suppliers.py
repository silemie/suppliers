"""
Test cases for Suppliers Model

Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Supplier, DataValidationError
from service import app
# from flask_mongoengine import MongoEngine
from mongoengine import connect

# DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://postgres:passw0rd@localhost:5432/postgres')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestSuppliers(unittest.TestCase):
    """ Test Cases for Suppliers """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database


    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):      
        db = connect('mydatabase')
        db.drop_database('mydatabase')
        # self.app = app.test_client()
        # db.drop_database('test')

    def tearDown(self):
        db.disconnect('mydatabase')
        db.drop_database('mydatabase')

    def test_serialize_a_supplier(self):
    #     """ Test serialization of a Supplier """
    #     supplier = Supplier(supplierName="Walmart", address="NYC", averageRating=5, productIdList = [1,2,3])
    #     data = supplier.serialize()
    #     self.assertNotEqual(data, None)
    #     self.assertIn('supplierID', data)
    #     self.assertEqual(data['supplierID'], None)
    #     self.assertIn('supplierName', data)
    #     self.assertEqual(data['supplierName'], "Walmart")
    #     self.assertIn('address', data)
    #     self.assertEqual(data['address'], "NYC")
    #     self.assertIn('averageRating', data)
    #     self.assertEqual(data['averageRating'], 5)
        pass

    def test_deserialize_a_pet(self):
    #     """ Test deserialization of a Supplier """
    #     data = {"supplierID": 1, supplierName:"Walmart", address:"NYC", averageRating:5, productIdList : [1,2,3]}
    #     supplier = Supplier()
    #     supplier.deserialize(data)
    #     self.assertNotEqual(supplier, None)
    #     self.assertEqual(supplier.supplierID, None)
    #     self.assertEqual(supplier.supplierName, "Walmart")
    #     self.assertEqual(supplier.address, "NYC")
    #     self.assertEqual(supplier.averageRating, 5)
    #     self.assertEqual(supplier.productIdList, [1,2,3])
        pass

    def test_create_a_supplier(self):
        """ Create a supplier and assert that it exists """
        supplier = Supplier(supplierName="Walmart", address="NYC", averageRating=5, productIdList = [1,2,3])
        self.assertTrue(supplier != None)
        self.assertEqual(supplier.supplierID, None)
        self.assertEqual(supplier.supplierName, "Walmart")
        self.assertEqual(supplier.address, "NYC")
        self.assertEqual(supplier.averageRating, 5)
        self.assertEqual(supplier.productIdList, [1,2,3])

    def test_add_a_supplier(self):
        """ Create a supplier and add it to the database """
        # suppliers = Supplier.all()
        # self.assertEqual(suppliers, [])
        # supplier = Supplier(supplierName="Walmart", address="NYC", averageRating=5, productIdList = [1,2,3])
        # self.assertTrue(supplier != None)
        # self.assertEqual(supplier.supplierID, None)
        # supplier.save()
        # # Asert that it was assigned an id and shows up in the database
        # self.assertEqual(supplier.id, 1)
        # suppliers = Supplier.all()
        # self.assertEqual(len(suppliers), 1)
        pass

    def test_update_a_supplier(self):
    #     """ Update a supplier """
    #     supplier = Supplier(supplierName="Walmart", address="NYC", averageRating=5, productIdList = [1,2,3])
    #     supplier.save()
    #     self.assertEqual(supplier.supplierID, 1)
    #     # Change it an save it
    #     supplier.supplierName = "Costco"
    #     supplier.save()
    #     self.assertEqual(supplier.supplierID, 1)
    #     # Fetch it back and make sure the id hasn't changed
    #     # but the data did change
    #     suppliers = Supplier.all()
    #     self.assertEqual(len(suppliers), 1)
    #     self.assertEqual(suppliers[0].supplierName, "Walmart")
        pass

    def test_find_supplier(self):
        """ Find a supplier by ID """
        pass
