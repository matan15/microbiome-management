import os
import dotenv
from typing import Dict


def get_google_creds() -> Dict:
    # Find and load .env file
    dotenv.load_dotenv(dotenv.find_dotenv())

    # return google creds as a dict
    return {
        "type": os.environ.get("type"),
        "project_id": os.environ.get("project_id"),
        "private_key_id": os.environ.get("private_key_id"),
        "private_key": os.environ.get("private_key"),
        "client_email": os.environ.get("client_email"),
        "clinet_id": os.environ.get("client_id"),
        "auth_uri": os.environ.get("auth_uri"),
        "token_uri": os.environ.get("token_uri"),
        "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": os.environ.get("client_x509_cert_url"),
        "universe_domain": os.environ.get("universe_domain"),
    }
