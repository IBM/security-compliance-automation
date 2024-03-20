# What is this script for?

This script is self-explanatory. It is used to create a Trusted Profile, that the user can register as a target in an SCC instance, to utilize SCC cross-account scan capabilities.

## Steps to run

1. Export all the required environment variables.

```
export CROSS_ACCOUNT_AUTH_URL=https://iam.cloud.ibm.com
export CROSS_ACCOUNT_URL=https://iam.cloud.ibm.com
export CROSS_ACCOUNT_AUTHTYPE=iam
export CROSS_ACCOUNT_APIKEY=<REPLACE THE VALUE WITH API KEY OF ACCOUNT WHERE YOU ARE CREATING THE TRUSTED PROFILE>
export TARGETS_ENDPOINT="https://region.compliance.cloud.ibm.com/instances/instance_id/v3/targets"
export TARGETS_URL=https://iam.cloud.ibm.com
export TARGETS_AUTHTYPE=iam
export TARGETS_APIKEY=<REPLACE THE VALUE WITH API KEY OF ACCOUNT OF WHICH ACCOUNT YOU ARE TRYING TO REGISTER AS CROSS ACCOUNT>
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