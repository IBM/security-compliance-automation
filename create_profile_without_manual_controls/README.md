# Custom Control Library and Profile Creation Script

This script automates the creation of custom control libraries and profiles based on predefined entities. The script performs the following tasks:
1. Retrieves predefined entities.
2. Removes manual controls.
3. Creates custom control library.
4. Creates custom profile.

## Dependencies
Ensure `parameter.json` exists with the required parameters.
```
Example - 
{
  "IBMCLOUD_API_TOKEN": "hjkhczjsjbfsbfsj",
  "SCC_INSTANCE_ID": "c03c755-76dd-4941-8566",
  "BASE_PROFILE_ID": "c13c755-76dd-4941-8566",
  "COMMAND_CENTER_URL": "https://us-south.compliance.cloud.ibm.com"

}
```

## Main Execution

The script reads parameters from a JSON file, retrieves predefined profile and control library details, removes manual controls, creates a custom control library, and finally creates a custom profile.

### Usage

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd create_profile_without_manual_controls
    ```

2. Create and activate a virtual environment:

    ```bash
    virtualenv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Ensure `parameter.json` exists with the required parameters. 

5. Run the `create_entities.py` script:
    
    ```bash
    python create_entities.py
    ```

