# Python 3 API Server on App Engine Standard

**OpenAPI-enabled Flask webserver to server both angular app (static files) and  overlaysAPI**

Steps to set up dev environment (windows) and deploy to app engine.
I used Windows10 :( bash shell so there would be changes for linux/MacOS.

## Google Cloud SDK
- Download and install the SDK. Keep it up to date.
- I chose to install it to user, instead of system, so as to avoid need for admin to install packages.
- This will probably also install python.

## Install Python 3.7 and PIP
Specifically, I had to:
- Check that python --version returns 3.7+
- Connexion requires Python 3.5.2+
- Upgrade pip with python -m pip in

## Create a venv and activate it
From git bash
```
cd api
python -m venv sandpit
cd sandpit/Scripts
. activate
python --version
cd ..
  ```

## OpenApi generator
Originally, I generated a Python3 Flask WServer from an OpenApi spec.
However, you should not need to do this, since the flask server is now in this repo.
```
cd  yarraheritagemaps\server'
openapi-generator generate -i overlays-api.yaml -g python-flask -o .
```
This server was generated by the [OpenAPI Generator](https://openapi-generator.tech) project. By using the
[OpenAPI-Spec](https://openapis.org) from a remote server, you can easily generate a server stub.  This
is an example of building a OpenAPI-enabled Flask server.

This example uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.


## Install API Credentials Client Library
If you are using a new GCP project, create a new credentials to access the BigQuery resources.
- Follow the Quickstart: Using Client Libraries [instructions](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries#client-libraries-install-python)

- Enable BigQuery API
- Create a Service Account. I used: bigquerypublicdataserviceacct@yarrascrape.iam.gserviceaccount.com
- In GCP console, apply these permissions to the service account.
-- BigQuery Data Viewer
-- BigQuery Job User
-- BigQuery Metadata Viewer

## Create a Private Key to run server locally
- Create a Private Key with BQ permissions. Permissions can be changed later from the GCP console IAM.
- Copy key to a subfolder 'secrets' of the app. Ensure this is not included in GIT repo.
- Add the subfolder to .gitignore

```bash
cd server
md secrets
cp /downloads/[mykey-name].json secrets
```

This key is required when the server runs locally so it can access the resources in the GCP project. 
When the server is running on app engine in the same project, the key is not used as it is already connected.

~Before running the server locally, set the environment to point to the key~.
This env is now added to main.py. so it should work.
You may need to update the path and keyname.

Bash shell

```bash
export GOOGLE_APPLICATION_CREDENTIALS="C:/yarrascrapy/yarraplanning/yarraheritagemaps/server/secrets/yarrascrape-b30815080477.json"
```

CMD shell

```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\yarrascrapy\yarraplanning\yarraheritagemaps\server\secrets\yarrascrape-b30815080477.json
```



## Configure VSCODE to point to the virtual environment

- This is necessary so the debugger and linter works correctly in the VSCODE IDE
- Edit settings.json and add this line, if the venv is called server.

```json
{
    "python.pythonPath": "server\\Scripts\\python.exe",
}
```
- Reload VSCODE with Ctrl-Shift-P and select Developer:Reload Window
- In _overlays_controller.py_, confirm the imports resolve (peek definition works)
Sometimes VSCODE pick up a new Venv when it is activated.

## Create Virtual Environment and Install Libraries

```bash
. /installserver.sh
```

- This script will activate the virtual environment then install the python libraries in requirements.txt.


## Run the server locally
To run the server, please execute the following from the root directory. This will activate the venv and execute main.py
If it fails with a library not found, check the venv is activated.

```bash
    npm run server
```

## Testing
Test it from another shell or POSTMAN

```bash
curl --request GET --header "Content-Type: application/json"  http://localhost:8080
curl --request GET --header "Content-Type: application/json"  http://localhost:8080/overlays/HO330
curl --request GET --header "Content-Type: application/json"  http://localhost:8080/openapi.yaml
```
The first command should return index.html
The next command should return json data.
The third command should return the overlays openapi specification in yaml form. (json also supported)

To launch the integration tests, use tox:

```
sudo pip install tox
tox
```

## Build a production verison of the app
angular.json is configured to place the compiled output files into server/app
The Flask server is configured to server static files from there.
app.yaml includes routes to serve static files as expected by an angular client.

The development version (npm start) is configured to call the local overlays-api at http://localhost:8080

The production version is configured to call the local overlays-api at https://yarrascrape.appspot.com

```bash
    npm run build
```

## Addendum - Running with Docker

If you want to change to App Engine Flexible Environment then you could deploy with docker.
To run the server on a Docker container, execute the following from the root directory:

```bash
# building the image
docker build -t openapi_server .

# starting up a container
docker run -p 8080:8080 openapi_server
```