from tkinter import simpledialog
from tkinter.messagebox import askyesno

def get_config():
    with open(".env", 'w') as envFile:
        envFile.write("")

    with open(".env", 'r') as envFile:
        initial_content = envFile.read()

    if "cloud_id" in initial_content and "user" in initial_content and "password" in initial_content and "API_KEY" in initial_content:
        return

    with open(".env", 'a') as envFile:
        if not 'ELASTIC' in initial_content:
            envFile.write("# ELASTICSEARCH\n")
            cloud_id = simpledialog.askstring("Configure credentials", "Enter the cloud Id:")
            while not cloud_id:
                answer = askyesno("Not valid value", "You have been entered a not valid value, do you want to enter a new value (yes) or exit (no)?")
                if answer:
                    cloud_id = simpledialog.askstring("Configure credentials", "Enter the cloud Id:")
                else:
                    exit()
            envFile.write("cloud_id=" + cloud_id + "\n")
            user = simpledialog.askstring("Configure credentials", "Enter the user name in Kibana:")
            while not user:
                answer = askyesno("Not valid value", "You have been entered a not valid value, do you want to enter a new value (yes) or exit (no)?")
                if answer:
                    user = simpledialog.askstring("Configure credentials", "Enter the user name in Kibana:")
                else:
                    exit()
            envFile.write("user=" + user + "\n")
            password = simpledialog.askstring("Configure credentials", "Enter the password in Kibana:")
            while not password:
                answer = askyesno("Not valid value", "You have been entered a not valid value, do you want to enter a new value (yes) or exit (no)?")
                if answer:
                    password = simpledialog.askstring("Configure credentials", "Enter the password in Kibana:")
                else:
                    exit()
            envFile.write("password=" + password + "\n")


        if not 'IMS' in initial_content:
            envFile.write("# IMS\n")
            api_key = simpledialog.askstring("Configure credentials", "Enter the IMS secret token:")
            while not api_key:
                answer = askyesno("Not valid value", "You have been entered a not valid value, do you want to enter a new value (yes) or exit (no)?")
                if answer:
                    api_key = simpledialog.askstring("Configure credentials", "Enter the IMS secret token:")
                else:
                    exit()
            envFile.write(f'API_KEY="{api_key}"\n')