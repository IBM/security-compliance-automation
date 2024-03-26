# What is this script for?

This script is used to create a Trusted Profile, that you can register as a target in a Security and Compliance Center instance, to utilize the cross account scan capabilities.

## Steps to run

1. Export all the required environment variables.

```
export CROSS_ACCOUNT_AUTH_URL=https://iam.cloud.ibm.com \
  CROSS_ACCOUNT_AUTHTYPE=iam \
  CROSS_ACCOUNT_APIKEY=<REPLACE THE VALUE WITH API KEY OF ACCOUNT WHERE YOU ARE CREATING THE TRUSTED PROFILE> \
  TARGETS_ENDPOINT=https://region.compliance.cloud.ibm.com/instances/instance_id/v3/targets \
  TARGETS_AUTH_URL=https://iam.cloud.ibm.com \
  TARGETS_AUTHTYPE=iam \
  TARGETS_APIKEY=<REPLACE THE VALUE WITH API KEY OF ACCOUNT OF WHICH ACCOUNT YOU ARE TRYING TO REGISTER AS CROSS ACCOUNT>
```

2. Run the installations of required packages:

   ```
   pip install -r requirements.txt
   ```

3. Run the script file:

   ```
   python create_trusted_profile_cross_account.py
   ```

4. Review the input requests and provide the required information.