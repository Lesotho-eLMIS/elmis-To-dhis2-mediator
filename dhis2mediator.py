import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import json

load_dotenv()

app = Flask(__name__)

# Configuration for DHIS2
## Remember to add a .env file with the following environment variables to the current directory
DHIS2_URL = os.getenv('DHIS2_URL')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
DHIS2_USERNAME = os.getenv('DHIS2_USERNAME')
DHIS2_PASSWORD = os.getenv('DHIS2_PASSWORD')
DATASET_ID = os.getenv('DATASET_ID') #elmis Indicators
ORG_UNIT_ID = os.getenv('ORG_UNIT_ID') # AHF
PERIOD = '202410'  # Example period
TOKEN_URL = os.getenv('TOKEN_URL')


def get_access_token():
    token_url = TOKEN_URL
    response = requests.post(
        token_url,
        data={
            'grant_type': 'password',
            'username': DHIS2_USERNAME,
            'password': DHIS2_PASSWORD
        },
        headers={'Accept': 'application/json'},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    
    response_data = response.json()
    access_token = response_data.get('access_token')
    
    if access_token:
        print("Access Token obtained successfully.")
    else:
        print("Failed to obtain access token:", response_data)
    
    return access_token

@app.route('/dhis2', methods=['POST'])
def dhis2():
    # Get the data from the request
    data = request.json

    # Transform data to DHIS2 format
    dhis2_data = {
        "dataSet": DATASET_ID,
        "completeDate": "2023-07-30",
        "period": PERIOD,
        "orgUnit": ORG_UNIT_ID,
        "dataValues": []
    }

    for key, value in data.items():
        dhis2_data["dataValues"].append({
            "dataElement": key,  # Assuming the key in your JSON matches the data element ID in DHIS2
            "value": value
        })

    # Log the transformed data for debugging
    print("Transformed data for DHIS2:", dhis2_data)

    # Obtain an access token
    access_token = get_access_token()

    if not access_token:
        return jsonify({"status": "error", "message": "Failed to obtain access token"}), 500

    try:
        # Send the data to DHIS2
        response = requests.post(
            DHIS2_URL,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps(dhis2_data)
        )

        # Log the response from DHIS2
        print("Response from DHIS2:", response.text)

        # Return the response from DHIS2
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Data sent to DHIS2 successfully"}), 200
        else:
            return jsonify({"status": "error", "message": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=67670)
