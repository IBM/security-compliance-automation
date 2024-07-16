from utils import base_utility, create_profile


def get_predefined_entities(params, entity_type, entity_id):
    response = base_utility.make_api_call(params, entity_type, entity_id, "GET", "")
    return response


def remove_manual_controls(controls):
    # Extract all level 1 control_parent references
    control_parent_references = {control["control_parent"] for control in controls}
    # Identify level 2controls to which are referred as parent control in other child controls
    controls_to_include = {
        control["control_name"]
        for control in controls
        if control["control_parent"] == "" or control["control_name"] in control_parent_references
    }
    # Filter controls: include those in controls_to_include or that don't match the exclusion criteria
    _filtered_controls = [
        control for control in controls
        if control["control_name"] in controls_to_include or not (
                control["control_specifications"] == [] and control["control_parent"] != ""
        )
    ]
    return _filtered_controls


def create_custom_control_library(_filtered_controls, control_lib_name, api_params):
    data = base_utility.prepare_control_lib_payload(_filtered_controls, control_lib_name)
    create_custom_lib_response = base_utility.make_api_call(api_params, "control_libraries", "", "POST", data)
    _custom_control_lib_id = create_custom_lib_response.get('id')
    return _custom_control_lib_id


def create_custom_profile(_custom_control_lib_id, profile_name, _default_parameters, api_params):
    data = create_profile.prepare_custom_profile_payload(_custom_control_lib_id, profile_name, _default_parameters)
    create_profile_response = base_utility.make_api_call(api_params, "profiles", "", "POST", data)


if __name__ == "__main__":
    parameter_file_path = "parameter.json"
    params = base_utility.read_parameters(parameter_file_path)

    # Get predefined profile details
    predefined_profile_response = get_predefined_entities(params, "profiles", params.get('BASE_PROFILE_ID'))
    predefined_control_lib_id = predefined_profile_response.get('controls')[0].get('control_library_id')

    # Get predefined control library details
    predefined_control_lib_response = get_predefined_entities(params, "control_libraries", predefined_control_lib_id)

    # Remove manual controls
    filtered_controls = remove_manual_controls(predefined_control_lib_response.get('controls'))

    # Create custom control library
    custom_control_lib_id = create_custom_control_library(filtered_controls,
                                                          predefined_control_lib_response.get('control_library_name'),
                                                          params)

    # Create custom profile
    default_parameters = predefined_profile_response.get('default_parameters', None)
    create_custom_profile(custom_control_lib_id, predefined_profile_response.get('profile_name'), default_parameters,
                          params)
