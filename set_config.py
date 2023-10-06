import sys
import os

parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir)

from termcolor import colored

def get_config():
    prompt_style = colored("What is the {}? ", "white", attrs=["bold"])
    if not os.path.exists(f"{parent_dir}/AWS/config.py"):
        host = input(prompt_style.format("Open Search host"))
        user = input(prompt_style.format("Open Search user name"))
        password = input(prompt_style.format("Open Search password"))
        port = input(prompt_style.format("Open Search Port"))

        with open('./AWS/config.py', 'w') as configfile:
            configfile.write(f"""ES_host = "{host}"
ES_user = "{user}"
ES_password = "{password}"
ES_port = {port}""")
        print(colored("Configuration saved to config.py", "green", attrs=["bold"]))
    else:
        print(colored("Configuration already exists, you can start upload the data.", "green", attrs=["bold"]))
    

if __name__ == "__main__":
    
    get_config()