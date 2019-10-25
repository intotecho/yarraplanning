echo Run from yarrraheritagemaps/ folder
echo Create Python environment to build the server.
python -m venv server
cd server/Scripts
. activate
cd ..
pip install --upgrade -r requirements.txt
# Following is required to run locally.
export GOOGLE_APPLICATION_CREDENTIALS=C:/yarrascrapy/yarraplanning/yarraheritagemaps/server/secrets/yarrascrape-b30815080477.json
cd ../
echo $ Now build anugular dist into ./app with npm run build. Then deploy to cloud with npm run deploy. 
