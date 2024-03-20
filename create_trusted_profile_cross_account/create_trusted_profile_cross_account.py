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

class CreateTrustedProfileAndCrossAccount(object):
    def __init__(self):
        try:
            self.service_client = IamIdentityV1.new_instance(service_name="CROSS_ACCOUNT")
            self.policy_service_client = IamPolicyManagementV1.new_instance(service_name="CROSS_ACCOUNT")
            apieky = os.getenv("TARGETS_APIKEY")
            url = os.getenv("TARGETS_URL")
            self.token_manager = IAMTokenManager(apikey=apieky,url=url)
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
            err = f"An error occurred while creating the trusted profile: {e}"
            self.colored_print(err,Colors.RED)

        try:
            crn = tpBody.get("crn")
            if crn != '':
                self.colored_print(f'Start setting crn - {crn} to the trusted profile, Please wait it will take some time ...',Colors.YELLOW)
                self.service_client.set_profile_identity(profile_id=tpProfile['id'],identity_type="crn",identifier=crn,type="crn",description=tpBody.get("crn_description"))
                self.colored_print("Successfully set the crn to the creating trusted profile.",Colors.GREEN)

            try:
                self.colored_print('Start assigning the required access policies for the trusted profile, Please wait it will take some time ...',Colors.YELLOW)
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

                self.colored_print("Successfully assigned the required access policies for the trusted profile.",Colors.GREEN)
                self.colored_print(f"Your trusted profile - {tpProfile['id']} is ready to utilize.",Colors.GREEN)
            except Exception as e:
                err = f"An error occurred while creating trusted profile: {e}"
                self.colored_print(err,Colors.RED)
                self.service_client.delete_profile(profile_id=tpProfile['id'])
                self.colored_print(f"Created trusted profile - {tpProfile['id']} was deleted due to unsucessful operations.",Colors.GREEN)
        except Exception as e:
            err = f"An error occurred while creating trusted profile: {e}"
            self.colored_print(err,Colors.RED)
            self.service_client.delete_profile(profile_id=tpProfile['id'])
            self.colored_print(f"Created trusted profile - {tpProfile['id']} was deleted due to unsucessful operations.",Colors.GREEN)

    def register_cross_account(self, api_endpoint_url, target_req_body,token):
        access_token = token['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(api_endpoint_url, headers=headers,json=target_req_body)

            if response.status_code == 201:
                self.colored_print(f"\nSuccessfully registered the cross account {target_req_body.get('account_id')}\n", Colors.GREEN)
                print(f"Response: {response.json()}")
            else:
                self.colored_print(f"Error: API request failed with status code {response.status_code}, error: {response.text}\n", Colors.RED)
        except Exception as e:
            self.colored_print(f"Error: {e}", Colors.RED)

    def register_cross_accounts(self,csv_file_path,token):
        expected_columns = ['name', 'account_id', 'trusted_profile_id','region','instance_id']

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

    ct.colored_print("\nChoose an action type from below you want to perform ... \n",Colors.CYAN)
    ct.colored_print("1. Create Trusted Profile", Colors.MAGENTA)
    ct.colored_print("2. Register Cross Account", Colors.MAGENTA)
    ct.colored_print("3. Register Multiple Cross Accounts From CSV", Colors.MAGENTA)

    actionType = ct.colored_input("\nEnter the number of your choice: ", Colors.MAGENTA)
    print('\n')
    if actionType == "1":
        ct.colored_print("Please provide the details which are required to create a trusted profile ...", Colors.CYAN)
        print('\n')
        account_id = ct.colored_input("Enter the account id in which you want create Trusted Profile: ", Colors.MAGENTA)
        print('\n')
        name = ct.colored_input("Enter the name for trusted profile you want to create: ", Colors.MAGENTA)
        print('\n')
        description = ct.colored_input("Enter the description for your trusted profile: ", Colors.MAGENTA)
        print('\n')
        crn = ct.colored_input("Enter the instance crn you want to utilize: ", Colors.MAGENTA)
        print('\n')
        crn_description = ct.colored_input("Enter the description for instance crn you want to utilize: ", Colors.MAGENTA)
        print('\n')
        tpBody = {"name": name, "description": description, "account_id":account_id, "crn": crn, "crn_description":crn_description}
        ct.colored_print("Initiate the creation of trusted profile, please wait for some time...", Colors.YELLOW)
        ct.create_trusted_profile(tpBody)
    elif actionType == "2":
        api_endpoint_url=os.getenv('TARGETS_ENDPOINT')
        ct.colored_print("Please provide the required details to create the target account ...", Colors.CYAN)
        print('\n')
        ct.colored_print("\nChoose region to register target account: \n",Colors.CYAN)
        if '.test.' in api_endpoint_url:
            regions = ['us-south_Dallas','us-east_Washington DC']
        else:
            regions = ['us-south_Dallas','au-syd_Sydney','ca-tor_Toronto','eu-de_Frankfurt','eu-es_Madrid','eu-fr2_BNPP']
        for index, region in enumerate(regions):
            region = region.split('_')
            txt = f"{index+1}: {region[1]} ({region[0]})\n"
            ct.colored_print(txt, Colors.MAGENTA)
        regionChoice = int(ct.colored_input("\nEnter the number of your choice: ", Colors.MAGENTA))
        while(len(regions) < regionChoice):
            regionChoice = int(ct.colored_input("\nEntered choice is invalid, please provide a valid number for your choice: ",Colors.RED))
        region = regions[regionChoice-1].split('_')[0]

        instance_id = ct.colored_input("\nEnter the security and compliance instance ID to register your cross account: ", Colors.MAGENTA)
        while(ct.is_valid_instance(instance_id)==False):
            instance_id = ct.colored_input("\nEntered security and compliance instance ID is invalid, please provide the valid security and compliance instance ID: ", Colors.RED)

        api_endpoint_url=api_endpoint_url.replace('region',region).replace('instance_id',instance_id)

        name = ct.colored_input("\nEnter the name to register cross account: ", Colors.MAGENTA)
        account_id = ct.colored_input("\nEnter the account id to register cross account: ", Colors.MAGENTA)
        trusted_profile_id = ct.colored_input("\nEnter the trusted profile id to access account's resources: ", Colors.MAGENTA)

        target_req_body ={"account_id":account_id,"trusted_profile_id":trusted_profile_id,"name":name}
        token = ct.token_manager.request_token()
        ct.colored_print("Registering cross account, please wait for some time...", Colors.YELLOW)
        ct.register_cross_account(api_endpoint_url,target_req_body,token)
    elif actionType == "3":
        csv_file_path = ct.colored_input("Provide the csv file path to register cross accounts: ", Colors.MAGENTA)
        token = ct.token_manager.request_token()
        ct.colored_print("Registering multiple cross accounts, please wait for some time...", Colors.YELLOW)
        ct.register_cross_accounts(csv_file_path,token)
    else:
        ct.colored_print("The selected action type is invalid, please re-initiate the script and give a valid action type.",Colors.RED)