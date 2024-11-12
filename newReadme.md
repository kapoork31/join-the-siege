

## Getting Started
1. Clone the repository:
    ```shell
    git clone <repository_url>
    cd join-the-siege
    ```

2. Install dependencies:
    ```shell
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

To run the app you must place AWS credentials into the .env file where they are currently commented out
You will need an access key , secrey key, region can be left as is and then fill these values into the .env file

In prod setting .env file would be injected into the container on startup in the docker run command and not baked in like I have done it which is bad practice

Run the APP
3a - easier
- run via <uvicorn src.fastapi_app:app --reload>
- will deploy the app on your pc
- view docs at http://127.0.0.1:8000/docs

3b - longer since docker build can take time as I have not made the docker container as small as possible
<docker build -t fastapi-app .>
<docker run -d -p 8080:8080 --name fastapi-app fastapi-app>
view docs at <http://localhost:8080/docs>

4. Test using jupyter notebook
- inside the venv run <pip install jupyter>
- run jupyter from the root of the directory, browser UI should open up and go to the notebooks folder and open api_test.ipynb
- run the cells to test the api
- diff urls are present for when dealing with docker vs non docker deployment


4. Test the classifier using a tool like curl:
using url with docker container url
to change curl commands to work with non docker deployment switch url from http://localhost:8080 to http://127.0.0.1:8000

run from root directory

step 1 upload a file
curl -X POST   'http://localhost:8080/upload_file/?customer_id=123'   -H 'accept: application/json'   -H 'Content-Type: multipart/form-data'   -F 'file=@notebooks/new_invoice1.txt'

step 2 classify a file
curl -X POST "http://localhost:8080/classify_file" \
  -H "Content-Type: application/json" \
  -d '{"filename": "new_invoice1.txt", "customer_id": 123}'

step 3 view file 
curl -X GET "http://localhost:8080/get_file?filename=new_invoice1.txt&customer_id=123" \
  -H "accept: application/json"


5. Run tests:
    pytest
