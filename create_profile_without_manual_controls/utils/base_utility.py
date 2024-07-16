import requests
import json


def read_parameters(parameter_file):
    try:
        with open(parameter_file, 'r') as f:
            params = json.load(f)
            return params
    except FileNotFoundError:
        print(f"Parameter file '{parameter_file}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in parameter file: {e}")
        return None


def make_api_call(params, entity_name, entity_id, method, payload):
    token = params.get('IBMCLOUD_API_TOKEN')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    try:
        # Get Details for Predefine Entity
        if method == "GET":
            api_url = params.get('COMMAND_CENTER_URL') + "/instances/" \
                      + params.get('SCC_INSTANCE_ID') + "/v3/" + entity_name + "/" + entity_id
            response = requests.get(api_url, headers=headers)
            print("Getting Predefined entity Details from  ", api_url)

        # Create Custom entity
        if method == "POST":
            api_url = params.get('COMMAND_CENTER_URL') + "/instances/" \
                      + params.get('SCC_INSTANCE_ID') + "/v3/" + entity_name
            print("Creating New " + entity_name + " - ", api_url)
            response = requests.post(api_url, payload, headers=headers)

        # Check if the request was successful (status code 2xx)
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            print(f"API call failed for file: {api_url} with status code {response.status_code}")

    except requests.RequestException as e:
        print(f"Error making API request for file {api_url}: {e}")


def prepare_control_lib_payload(filtred_controls, control_lib_name):
    data = {
        "control_library_name": control_lib_name,
        "control_library_description": control_lib_name,
        "control_library_type": "custom",
        "control_library_version": "0.0.1",
        "latest": True,
        "controls": filtred_controls
    }
    with open('output/custom_library.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    return json.dumps(data)
