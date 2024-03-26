import os
import csv
import uuid
from ibm_platform_services import IamIdentityV1,IamPolicyManagementV1,iam_policy_management_v1
from ibm_cloud_sdk_core import IAMTokenManager
import requests

class Colors:
    RED = "31"
    GREEN = "32"
    YELLOW = "33"
    MAGENTA = "35"
    CYAN = "36"
    RESET = "0"

class CreateTrustedProfileAndCrossAccount(object):
    def __init__(self):
        try:
            self.service_client = IamIdentityV1.new_instance(service_name="CROSS_ACCOUNT")
            self.policy_service_client = IamPolicyManagementV1.new_instance(service_name="CROSS_ACCOUNT")
            apikey = os.getenv("TARGETS_APIKEY")
            url = os.getenv("TARGETS_AUTH_URL")
            self.token_manager = IAMTokenManager(apikey=apikey,url=url)
        except Exception as e:
           err = f'Error while creating instances for iam identity and policy services - {e}'
           self.colored_print(err,Colors.RED)

    def colored_input(self,prompt, color_code):
        return input(f'\033[{color_code}m{prompt}\033[0m')

    def colored_print(self,text, color_code):
        print(f'\033[{color_code}m{text}\033[0m')

    def is_valid_instance(self,instanceId):
        try:
            uuid_instance = uuid.UUID(instanceId, version=4)
            return str(uuid_instance) == instanceId
        except ValueError:
            return False

    def create_trusted_profile(self, tpBody):
        #tpProfile = None
        try:
            tpProfile = self.service_client.create_profile(name=tpBody.get("name"),description=tpBody.get("description"),account_id=tpBody.get("account_id")).get_result()
            self.colored_print(f"Trusted profile creation was successful - {tpProfile['id']}",Colors.GREEN)
        except Exception as e:
            err = f"An error occurred while creating the Trusted Profile: {e}"
            self.colored_print(err,Colors.RED)

        try:
            crn = tpBody.get("crn")
            if crn != '':
                self.colored_print(f'Start setting crn - {crn} to the Trusted Profile...',Colors.YELLOW)
                self.service_client.set_profile_identity(profile_id=tpProfile['id'],identity_type="crn",identifier=crn,type="crn",description=tpBody.get("crn_description"))
                self.colored_print("Successfully set the crn to the creating Trusted Profile.",Colors.GREEN)

            try:
                self.colored_print('Start assigning the required access policies for the Trusted Profile...',Colors.YELLOW)
                attribute=iam_policy_management_v1.SubjectAttribute(name='iam_id', value='iam-'+tpProfile['id']).to_dict()
                policy_subjects = iam_policy_management_v1.PolicySubject(attributes=[attribute])
                account_id_resource_attribute = iam_policy_management_v1.ResourceAttribute(name='accountId', value=tpBody.get("account_id"))

                iam_viewer_role = iam_policy_management_v1.PolicyRole(role_id='crn:v1:bluemix:public:iam::::role:Viewer')
                iam_configreader_role = iam_policy_management_v1.PolicyRole(role_id='crn:v1:bluemix:public:iam::::role:ConfigReader')
                iam_service_role_reader = iam_policy_management_v1.PolicyRole(role_id='crn:v1:bluemix:public:iam::::serviceRole:Reader')
                iam_admin_role = iam_policy_management_v1.PolicyRole(role_id='crn:v1:bluemix:public:iam::::role:Administrator')
                policy_roles = [
                                iam_service_role_reader,
                                iam_viewer_role,
                                iam_configreader_role
                            ]
                service_name_resource_attribute = iam_policy_management_v1.ResourceAttribute(name='serviceType', value='service')
                policy_resources = iam_policy_management_v1.PolicyResource(attributes=[account_id_resource_attribute, service_name_resource_attribute])
                self.policy_service_client.create_policy(
                type='access', subjects=[policy_subjects], roles=policy_roles, resources=[policy_resources]
                ).get_result()

                policy_roles = [
                                iam_service_role_reader,
                                iam_admin_role,
                                iam_configreader_role
                            ]
                service_name_resource_attribute = iam_policy_management_v1.ResourceAttribute(name='serviceName', value='containers-kubernetes')
                policy_resources = iam_policy_management_v1.PolicyResource(attributes=[account_id_resource_attribute, service_name_resource_attribute])
                self.policy_service_client.create_policy(
                type='access', subjects=[policy_subjects], roles=policy_roles, resources=[policy_resources]
                ).get_result()

                policy_roles = [iam_viewer_role,iam_configreader_role]
                service_name_resource_attribute = iam_policy_management_v1.ResourceAttribute(name='serviceType', value='platform_service')
                policy_resources = iam_policy_management_v1.PolicyResource(attributes=[account_id_resource_attribute, service_name_resource_attribute])
                self.policy_service_client.create_policy(
                type='access', subjects=[policy_subjects], roles=policy_roles, resources=[policy_resources]
                ).get_result()

                self.colored_print("Successfully assigned the required access policies for the Trusted Profile.",Colors.GREEN)
                self.colored_print(f"Your Trusted Profile - {tpProfile['id']} is ready to utilize.",Colors.GREEN)
            except Exception as e:
                err = f"An error occurred while creating Trusted Profile: {e}"
                self.colored_print(err,Colors.RED)
                self.service_client.delete_profile(profile_id=tpProfile['id'])
                self.colored_print(f"Created Trusted Profile - {tpProfile['id']} was deleted due to unsucessful operations.",Colors.GREEN)
        except Exception as e:
            err = f"An error occurred while creating Trusted Profile: {e}"
            self.colored_print(err,Colors.RED)
            self.service_client.delete_profile(profile_id=tpProfile['id'])
            self.colored_print(f"Created Trusted Profile - {tpProfile['id']} was deleted due to unsucessful operations.",Colors.GREEN)

    def register_cross_account(self, api_endpoint_url, target_req_body, token):
        access_token = token['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(api_endpoint_url, headers=headers,json=target_req_body)

            if response.status_code == 201:
                self.colored_print(f"Successfully registered the cross account {target_req_body.get('account_id')}", Colors.GREEN)
                print(f"Response: {response.json()}")
            else:
                self.colored_print(f"Error: API request failed with status code {response.status_code}, error: {response.text}\n", Colors.RED)
        except Exception as e:
            self.colored_print(f"Error: {e}", Colors.RED)

    def register_cross_accounts(self,csv_file_path,token):
        expected_columns = ['name', 'account_id', 'trusted_profile_id', 'region', 'instance_id']

        with open(csv_file_path, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            actual_columns = csv_reader.fieldnames
            if set(expected_columns) == set(actual_columns):
                api_endpoint_url=os.getenv('TARGETS_ENDPOINT')
                for row in csv_reader:
                    api_endpoint_url=os.getenv('TARGETS_ENDPOINT')
                    api_endpoint_url=api_endpoint_url.replace('region',row['region']).replace('instance_id',row['instance_id'])
                    target_req_body = {
                        'trusted_profile_id': row['trusted_profile_id'],
                        'account_id': row['account_id'],
                        'name': row['name']
                    }
                    self.register_cross_account(api_endpoint_url,target_req_body,token)
            else:
                self.colored_print("Error: not all expected columns are present in the CSV file.",Colors.RED)
                self.colored_print(f"Missing columns are: { set(expected_columns) - set(actual_columns)}",Colors.RED)

if __name__ == "__main__":
    ct = CreateTrustedProfileAndCrossAccount()

    ct.colored_print("\nChoose an action type from below you want to perform\n",Colors.CYAN)
    ct.colored_print("1. Create Trusted Profile", Colors.RESET)
    ct.colored_print("2. Register Cross Account", Colors.RESET)
    ct.colored_print("3. Register Multiple Cross Accounts From CSV", Colors.RESET)

    actionType = ct.colored_input("\nEnter the number of your choice: ", Colors.RESET)

    if actionType == "1":
        ct.colored_print("\nPlease provide the details which are required to create a Trusted Profile", Colors.CYAN)
        account_id = ct.colored_input("\nEnter the account ID in which you want create Trusted Profile: ", Colors.RESET)
        name = ct.colored_input("Enter the name for Trusted Profile you want to create: ", Colors.RESET)
        description = ct.colored_input("Enter the description for your Trusted Profile: ", Colors.RESET)
        crn = ct.colored_input("Enter the instance crn you want to utilize: ", Colors.RESET)
        crn_description = ct.colored_input("Enter the description for instance crn you want to utilize: ", Colors.RESET)
        tpBody = {"name": name, "description": description, "account_id":account_id, "crn": crn, "crn_description":crn_description}
        ct.colored_print("\nInitiate the creation of Trusted Profile...", Colors.YELLOW)
        ct.create_trusted_profile(tpBody)
    elif actionType == "2":
        api_endpoint_url=os.getenv('TARGETS_ENDPOINT')
        ct.colored_print("\nPlease provide the required details to create the target account", Colors.CYAN)
        ct.colored_print("\nChoose a region to register target account: \n",Colors.CYAN)
        regions = ['us-south_Dallas','ca-tor_Toronto','eu-de_Frankfurt','eu-es_Madrid']
        for index, region in enumerate(regions):
            region = region.split('_')
            txt = f"{index+1}: {region[1]} ({region[0]})"
            ct.colored_print(txt, Colors.RESET)
        regionChoice = int(ct.colored_input("\nEnter the number of your choice: ", Colors.RESET))
        while(len(regions) < regionChoice):
            regionChoice = int(ct.colored_input("The choice is invalid, please provide a valid number for your choice: ",Colors.RED))
        region = regions[regionChoice-1].split('_')[0]

        instance_id = ct.colored_input("Enter the Security and Compliance instance ID to register your cross account: ", Colors.RESET)
        while(ct.is_valid_instance(instance_id)==False):
            instance_id = ct.colored_input("The Security and Compliance instance ID is invalid, please provide the valid Security and Compliance instance ID: ", Colors.RED)

        api_endpoint_url=api_endpoint_url.replace('region',region).replace('instance_id',instance_id)

        name = ct.colored_input("Enter the name to register cross account: ", Colors.RESET)
        account_id = ct.colored_input("Enter the account ID to register cross account: ", Colors.RESET)
        trusted_profile_id = ct.colored_input("Enter the Trusted Profile ID to access account's resources: ", Colors.RESET)

        target_req_body ={"account_id":account_id,"trusted_profile_id":trusted_profile_id,"name":name}
        token = ct.token_manager.request_token()
        ct.colored_print("\nRegistering cross account...", Colors.YELLOW)
        ct.register_cross_account(api_endpoint_url,target_req_body,token)
    elif actionType == "3":
        csv_file_path = ct.colored_input("Provide the csv file path to register cross accounts: ", Colors.RESET)
        token = ct.token_manager.request_token()
        ct.colored_print("Registering multiple cross accounts...", Colors.YELLOW)
        ct.register_cross_accounts(csv_file_path,token)
    else:
        ct.colored_print("The selected action type is invalid, please re-initiate the script and give a valid action type.",Colors.RED)