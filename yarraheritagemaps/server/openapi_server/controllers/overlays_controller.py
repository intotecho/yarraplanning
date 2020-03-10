import connexion
import six
import flask
from flask_cors import CORS
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.overlay import Overlay  # noqa: E501
from openapi_server import util
import logging
import queries
from google.cloud import bigquery
import json

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
  # This is used when running locally only. When deploying use a webserver process 
  # such as Gunicorn to serve the app.
  app.run(host='127.0.0.1', port=8080, debug=True)

from flask import Flask, send_from_directory
app = Flask(__name__)

CORS(app)

DATASET = 'YarraPlanning'

#GOOGLE_APPLICATION_CREDENTIALS="C:/yarrascrapy/yarraplanning/yarraheritagemaps/api/sandpit/secrets/yarrascrape-b30815080477.json"
#from oauth2client.service_account import ServiceAccountCredentials
#scopes = ['https://www.googleapis.com/auth/bigquery']



def start_appengine(type=None):  # noqa: E501
    
    """App Engine Start Does nothing but causes 404 if not handled.

     # noqa: E501
    :rtype: String 
    """
    app.logger.info('Processing App Start  request')
    return 'Startup no-op'

def list_overlays(type=None):  # noqa: E501
    
    """List all overlays

     # noqa: E501
    :param type: heritage or other overlay types
    :type type: str
    :rtype: List[Overlay]
    """
    #credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes)
    app.logger.info('Processing default request')
 
    client = bigquery.Client()
    #client = bigquery.Client(credentials=credentials,  project="yarrascrape")
    query_job = client.query(queries.OVERLAYS_QUERY.format(DATASET))
    try:
      results = query_job.result() 
      #app.logger.error(results)
      jsondoc = []
      for row in results:
        item = {
          'Overlay': row.Overlay, 
          'HeritagePlace': row.HeritagePlace,
          'ZONE_DESC': row.ZONE_DESC,
          'PaintControls': row.PaintControls,
          'InternalControls': row.InternalControls,
          'TreeControls': row.TreeControls,
          'FenceControls': row.FenceControls,
          'Included': row.Included,
          'VHR': row.VHR,
          'Prohibited': row.Prohibited,
          'AboriginalHeritagePlace': row.AboriginalHeritagePlace,
          'Status': row.Status,
          'Expiry': row.Expiry,
          'bndry': row.bndry,
          'Image': row.Image
        }
        #app.logger.info(row.Overlay)
        jsondoc.append(item)
      return jsondoc 
    except IndexError:
      app.logger.error('No Overlays')
      return None

def show_overlay_by_id(overlay_id, infotype=None):  # noqa: E501
    """Info for a specific overlay
     # noqa: E501
    :param overlay_id: The id of the overlay to retrieve
    :type overlay_id: str
    :rtype: Overlay
    """
    app.logger.info('Processing request - Heritage Sitess in Overlay')
    client = bigquery.Client()
    if infotype=='planning':
      query_job = client.query(queries.PLANNING_APPS_QUERY.format(DATASET, overlay_id))
      try:
        results = query_job.result() 
        #app.logger.error(results)
        jsondoc = []
        for row in results:
          item = {
            'Application_Number': row.Application_Number, 
            'Property_Address': row.Property_Address,
            'Estimated_Cost': row.Estimated_Cost,
            'HeritageStatus': row.HeritageStatus,
            'Date_Received': row.Date_Received,
            'Description': row.Description,
            'Decision': row.Decision,
            'Application_Status': row.Application_Status,
            'Abandoned': row.Abandoned,
            'Refused': row.Refused,
            'Approved': row.Approved,
            'In_Progress': row.In_Progress,
            'dist_meters': row.dist_meters,
            'bndry': row.bndry
          }
          #app.logger.info(row.Overlay)
          jsondoc.append(item)
        return jsondoc
      except IndexError:
        app.logger.error('No Planning Applicationsin Overlay {}'.format(overlay_id))
        return []

    else:
      query_job = client.query(queries.HERITAGE_SITE_QUERY.format(DATASET, overlay_id))
      try:
        results = query_job.result() 
        #app.logger.error(results)
        jsondoc = []
        for row in results:
          item = {
            'Overlay': row.Overlay, 
            'Name': row.Name,
            'EZI_ADD': row.EZI_ADD,
            'row_num': row.row_num,
            'HeritageStatus': row.HeritageStatus,
            'vhdplaceid': row.vhdplaceid,
            'vhdPlacesId': row.vhdPlacesId,
            'Image': row.Image,
            'Authority': row.Authority,
            'PropertyType': row.PropertyType,
            'PROPNUM': row.PROPNUM,
            'OriginalAddress': row.OriginalAddress,
            'EstimatedDate': row.EstimatedDate,
            'vhdLocation': row.vhdLocation,
            'Matched': row.Matched,
            'VHR': row.VHR,
            'href': row.href,
            'SosHash': row.SosHash,
            'earliest': row.earliest,
            'bndry': row.bndry
          }
          #app.logger.info(row.Overlay)
          jsondoc.append(item)
        #json.JSONEncoder.default(    
        return jsondoc 
      except IndexError:
        app.logger.error('No Heritage Sites in Overlay {}'.format(overlay_id))
        return []
