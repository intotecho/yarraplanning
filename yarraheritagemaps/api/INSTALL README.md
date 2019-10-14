To install cloud endpoints, I had to follow the instructions here
https://cloud.google.com/endpoints/docs/frameworks/python/get-started-frameworks-python

Specifically, I had to:
- Remove python3.7 from the path. (user and system)
- Once python --version returns 2.7:
- Open Git Bash Terminal with Admin.
- Upgrade pip with python -m pip install --upgrade pip
- Install Visual Studio 9 C++ Compiler for python 2.7 from  http://aka.ms/vcpython27 
  This redirected to https://www.microsoft.com/en-us/download/confirmation.aspx?id=44266
- Run pip as a module as in 
python  -m pip install --target lib --requirement requirements.txt --ignore-install
- Running the next command failed.
python lib/endpoints/endpointscfg.py get_openapi_spec main.EchoApi --hostname [YOUR_PROJECT_ID].appspot.com
Install app engine - use the gcloud cmd tool, not bash shell. Then can generate the endpointscfg.py
Move the anhular app dist folder to a subfolder of the api and change the path to index.html etc.
