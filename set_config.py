from tkinter import simpledialog
from tkinter.messagebox import askyesno

def get_config():
    """
    Configure and generate the necessary environment variables for Elasticsearch and IMS API.

    This function prompts the user to enter required credentials such as cloud_id, user, password for Elasticsearch,
    and API_KEY for IMS API. It creates or updates the '.env' file with the provided values.

    If the '.env' file already contains valid credentials for both Elasticsearch and IMS API, the function does not
    prompt the user and exits.

    Returns:
        None
    """
    with open(".env", 'w') as envFile:
        envFile.write("")

    with open(".env", 'r') as envFile:
        initial_content = envFile.read()

    if "cloud_id" in initial_content and "user" in initial_content and "password" in initial_content and "API_KEY" in initial_content:
        return False

    with open(".env", 'a') as envFile:
        if not 'ELASTIC' in initial_content:
            envFile.write("# ELASTICSEARCH\n")
            cloud_id = simpledialog.askstring("Configure credentials", "Enter the cloud Id:")
            while not cloud_id:
                answer = askyesno("Not valid value", "You have been entered a not valid value, do you want to enter a new value (yes) or exit (no)?")
                if answer:
                    cloud_id = simpledialog.askstring("Configure credentials", "Enter the cloud Id:")
                else:
                    return False
            envFile.write("cloud_id=" + cloud_id + "\n")
            user = simpledialog.askstring("Configure credentials", "Enter the user name in Kibana:")
            while not user:
                answer = askyesno("Not valid value", "You have been entered a not valid value, do you want to enter a new value (yes) or exit (no)?")
                if answer:
                    user = simpledialog.askstring("Configure credentials", "Enter the user name in Kibana:")
                else:
                    return False
            envFile.write("user=" + user + "\n")
            password = simpledialog.askstring("Configure credentials", "Enter the password in Kibana:")
            while not password:
                answer = askyesno("Not valid value", "You have been entered a not valid value, do you want to enter a new value (yes) or exit (no)?")
                if answer:
                    password = simpledialog.askstring("Configure credentials", "Enter the password in Kibana:")
                else:
                    return False
            envFile.write("password=" + password + "\n\n")

        if not 'IMS' in initial_content:
            envFile.write("# IMS\n")
            api_key = simpledialog.askstring("Configure credentials", "Enter the IMS secret token:")
            while not api_key:
                answer = askyesno("Not valid value", "You have been entered a not valid value, do you want to enter a new value (yes) or exit (no)?")
                if answer:
                    api_key = simpledialog.askstring("Configure credentials", "Enter the IMS secret token:")
                else:
                    return False
            envFile.write(f'API_KEY="{api_key}"\n')