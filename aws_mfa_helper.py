import logging
import os

import boto3
import botocore
import botocore.session
from botocore import credentials

LOGGER = logging.getLogger(__name__)


def get_session(role_arn: str = None) -> boto3.Session:
    """
    Get's a boto3 session that's configured to use cached MFA credentials and has assumed the required role, if
    supplied, which makes dev & testing easier, as you're not prompted for an MFA token every execution and don't have
    to supply the temporary role credentials to every new client
    :param str role_arn: The ARN of the IAM role to assume
    :return: a boto3.Session configured to use cached MFA credentials
    """
    # Change the cache path from the default of ~/.aws/boto/cache to the one used by awscli
    mfa_cache_dir = os.path.join(os.path.expanduser('~'), '.aws/cli/cache')

    # Construct botocore session with cache
    botocore_session = botocore.session.get_session()
    provider = botocore_session.get_component('credential_provider').get_provider('assume-role')
    provider.cache = credentials.JSONFileCache(mfa_cache_dir)

    session_args = {'botocore_session': botocore_session}

    if role_arn:
        client = boto3.Session(**session_args).client('sts')
        response = client.assume_role(RoleArn=role_arn, RoleSessionName='publish_api_session')
        LOGGER.info('Obtained credentials for identity: %s', client.get_caller_identity()['Arn'])

        session_args['aws_access_key_id'] = response['Credentials']['AccessKeyId']
        session_args['aws_secret_access_key'] = response['Credentials']['SecretAccessKey']
        session_args['aws_session_token'] = response['Credentials']['SessionToken']

    return boto3.Session(**session_args)


def refresh_helpers():
    global sesh, ddb_c, ddb_r
    sesh = get_session()
    ddb_c = sesh.client('dynamodb')
    ddb_r = sesh.resource('dynamodb')


sesh = None
ddb_c = None
ddb_r = None
refresh_helpers()
