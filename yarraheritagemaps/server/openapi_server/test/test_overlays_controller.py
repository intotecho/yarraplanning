# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.overlay import Overlay  # noqa: E501
from openapi_server.test import BaseTestCase


class TestOverlaysController(BaseTestCase):
    """OverlaysController integration test stubs"""

    def test_list_overlays(self):
        """Test case for list_overlays

        List all overlays
        """
        query_string = [('type', 'type_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/overlays',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_show_overlay_by_id(self):
        """Test case for show_overlay_by_id

        Info for a specific overlay
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/overlays/{overlay_id}'.format(overlay_id='overlay_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
