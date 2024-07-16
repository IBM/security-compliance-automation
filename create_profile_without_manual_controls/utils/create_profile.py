import json


def read_json_to_map(filepath, key_index):
    with open(filepath) as file:
        data = json.load(file)
        control_list = data[key_index]
        return control_list


def extract_control_ids(control_lib_id, ctrl_id):
    return {
        "control_library_id": control_lib_id,
        "control_id": ctrl_id
    }


def generate_json(profile_name, profile_description, profile_version, controls, default_parameters):
    data = {
        "profile_name": profile_name,
        "profile_description": profile_description,
        "profile_version": profile_version,
        "controls": controls,
        "default_parameters": default_parameters
    }
    return data


# Read json file for Control ids
def prepare_custom_profile_payload(control_lib_id, profile_name, default_parameters):
    control_lib_file = "output/custom_library.json"
    key_column = 'controls'  # Replace with the name of the column you want to use as the key
    controls_list = read_json_to_map(control_lib_file, key_column)
    profile_name = profile_name
    profile_description = profile_name
    profile_version = "0.0.1"
    controls = []
    for control in controls_list:
        control_library_id = control_lib_id
        control_id = f"{control['control_id']}"
        controls.append(extract_control_ids(control_library_id, control_id))
    # Generate JSON data
    json_data = generate_json(profile_name, profile_description, profile_version, controls, default_parameters)
    # Save to a file
    with open('output/custom_profile.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    return json.dumps(json_data)
