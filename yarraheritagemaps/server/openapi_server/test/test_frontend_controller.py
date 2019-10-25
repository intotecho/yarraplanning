# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.test import BaseTestCase


class TestFrontendController(BaseTestCase):
    """FrontendController integration test stubs"""

    def test_go_home(self):
        """Test case for go_home

        home page.
        """
        headers = { 
            'Accept': 'text/html',
        }
        response = self.client.open(
            '/v1/',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
