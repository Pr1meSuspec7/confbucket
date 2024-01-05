#!/usr/bin/python3

""" Import modules """
import os
import yaml
import netmiko
import pandas as pd
import numpy as np
from git import Repo
from git.exc import GitCommandError
from datetime import datetime
from dotenv import dotenv_values
from colorama import Fore, Style


### Control functions ###


def backup_folder(folder):
    """function to check if backup folder exist and create it"""
    try:
        os.makedirs(folder)
        colored_green("backup folder: created")
    except FileExistsError:
        colored_yellow("backup folder: already exists")


def load_login_info(file):
    """function to load login info from .env file or from environment variables"""
    if os.path.exists(file) == True:
        credentials = dotenv_values(file)
        return credentials
    else:
        credentials = {
            "USERNAME": os.getenv("USERNAME"),
            "PASSWORD": os.getenv("PASSWORD"),
            "GIT_TOKEN": os.getenv("GIT_TOKEN"),
        }
        return credentials


def yaml_to_json(file):
    """function to convert yaml inventory to json inventory"""
    with open(file, "r", encoding="utf8") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
            return parsed_yaml
        except yaml.YAMLError as exc:
            print(exc)


def xls_to_json(file):
    """function to convert xls inventory to json inventory"""
    try:
        df = pd.read_excel(file).replace(np.nan, None)
        parsed_xls = df.to_dict("records")
        return parsed_xls
    except Exception as e:
        print(e)


def change_login_info(inventory):
    """Function to override credential when is 'None'"""
    for item in inventory:
        if item["username"] is None and item["password"] is None:
            item["username"] = credentials.get("USERNAME")
            item["password"] = credentials.get("PASSWORD")
    return inventory


def conf_to_file(file, data):
    """Function write conf to file"""
    with open("./backup/" + file, "w", encoding="utf8") as log_file:
        log_file.write(data)
        log_file.write("\n")


def summary_report(data):
    """Function to log summary report"""
    with open("summary.log", "a", encoding="utf8") as log_file:
        log_file.write(data)
        log_file.write("\n")


def clear_summary_report():
    """Function to clear log file"""
    with open("summary.log", "w", encoding="utf8") as summary_file:
        summary_file.close()


def colored_green(text):
    """Green color text"""
    print(Fore.GREEN + text + Style.RESET_ALL)


def colored_red(text):
    """Red color text"""
    print(Fore.RED + text + Style.RESET_ALL)


def colored_yellow(text):
    """Yellow color text"""
    print(Fore.YELLOW + text + Style.RESET_ALL)


### Git functions ###


def load_git_info(folder):
    """function to load git info from .git folder"""
    if os.path.isdir(folder) == True:
        global now
        global commit_message
        global repo_token
        global repo_folder
        global repo
        global repo_url
        global repo_token_url
        now = datetime.now().isoformat("@", "seconds")
        commit_message = "backup " + str(now)
        repo_token = credentials.get("GIT_TOKEN")
        repo_folder = "."
        repo = Repo(repo_folder)
        # repo_url = repo.remotes.origin.url.split("https://")[1]
        # repo_url = repo.remotes.origin.url.split("git@github.com:")[1]
        # repo_token_url = "https://" + repo_token + "@" + repo_url
        # repo_token_url = repo.remotes.origin.url
    else:
        pass


# def git_push(local_repo, msg, repourl_w_token):
def git_push(local_repo, msg):
    """function to push new config files on remote repo"""
    try:
        local_repo.git.add(".")
        local_repo.git.commit(m=msg)
        # local_repo.git.push(repourl_w_token)
        local_repo.git.push
        print("Committed")
    except GitCommandError:
        print("nothing to commit, working tree clean")
    except Exception as e:
        # decomment to debug
        # print(e)
        print("Some error occured while pushing the code")


### Backup functions ###


def backup_ios(net_device):
    """function to get Cisco IOS running-config"""
    for n in range(2):
        try:
            net_connect = netmiko.ConnectHandler(**net_device)
            # print("Working on " + net_device['host'])
            filename = net_device["host"] + ".ios"
            showrun = net_connect.send_command("show run")
            conf_to_file(filename, showrun)
            output = net_device["host"] + ": OK"
            colored_green(output)
            summary_report(output)
        except Exception:
            output = (
                net_device["host"]
                + ": ERROR [Authentication failed or device unreachable]"
            )
            colored_red(output)
            summary_report(output)
            continue
        else:
            break


def backup_nxos(net_device):
    """function to get Cisco NXOS running-config and delete TimeStamp"""
    for n in range(2):
        try:
            net_connect = netmiko.ConnectHandler(**net_device)
            # print("Working on " + net_device['host'])
            filename = net_device["host"] + ".nxos"
            showrun = net_connect.send_command('show run | exclude "!Time:"')
            conf_to_file(filename, showrun)
            output = net_device["host"] + ": OK"
            colored_green(output)
            summary_report(output)
        except Exception:
            output = (
                net_device["host"]
                + ": ERROR [Authentication failed or device unreachable]"
            )
            colored_red(output)
            summary_report(output)
            continue
        else:
            break


def backup_iosxr(net_device):
    """function to get Cisco XR running-config and delete TimeStamp"""
    for n in range(2):
        try:
            net_connect = netmiko.ConnectHandler(**net_device)
            # print("Working on " + net_device['host'])
            filename = net_device["host"] + ".ios-xr"
            showrun = net_connect.send_command("show run")
            showrun = showrun.split("\n")[3:]  # remove first 3 lines
            showrun = "\n".join(showrun)  # rejoin list in string
            conf_to_file(filename, showrun)
            output = net_device["host"] + ": OK"
            colored_green(output)
            summary_report(output)
        except Exception:
            output = (
                net_device["host"]
                + ": ERROR [Authentication failed or device unreachable]"
            )
            colored_red(output)
            summary_report(output)
            continue
        else:
            break


def backup_junos(net_device):
    """function to get Junos running-config"""
    for n in range(2):
        try:
            net_connect = netmiko.ConnectHandler(**net_device)
            # print("Working on " + net_device['host'])
            filename = net_device["host"] + ".conf"
            showrun = net_connect.send_command("show configuration | display set")
            conf_to_file(filename, showrun)
            output = net_device["host"] + ": OK"
            colored_green(output)
            summary_report(output)
        except Exception:
            output = (
                net_device["host"]
                + ": ERROR [Authentication failed or device unreachable]"
            )
            colored_red(output)
            summary_report(output)
            continue
        else:
            break


def backup_bigip(net_device):
    """function to get BIG-IP running-config"""
    for n in range(2):
        try:
            net_connect = netmiko.ConnectHandler(**net_device)
            filename = net_device["host"] + ".conf"
            showrun = net_connect.send_command("show running-config")
            conf_to_file(filename, showrun)
            output = net_device["host"] + ": OK"
            colored_green(output)
            summary_report(output)
        except Exception:
            output = (
                net_device["host"]
                + ": ERROR [Authentication failed or device unreachable]"
            )
            colored_red(output)
            summary_report(output)
            continue
        else:
            break


########################


print(Style.BRIGHT + "\n*** RUNNING ***" + Style.RESET_ALL)

# clear summary.log file
clear_summary_report()

# create backup folder
backup_folder("./backup")

# import inventory and convert to json
devices = yaml_to_json("inventory.yaml")
# devices = xls_to_json("inventory.xlsx")

# import credential from .env or env vars
credentials = load_login_info(".env")

# use default login info or override with specific
devices = change_login_info(devices)

# if .git folder exist load parameters
load_git_info(".git")

# connect to the device w/ netmiko
for device in devices:
    if device["device_type"] == "cisco_ios":
        backup_ios(device)
    elif device["device_type"] == "cisco_nxos":
        backup_nxos(device)
    elif device["device_type"] == "cisco_xr":
        backup_iosxr(device)
    elif device["device_type"] == "juniper_junos":
        backup_junos(device)
    elif device["device_type"] == "f5_tmsh":
        backup_bigip(device)
    else:
        output_err = device["host"] + ": ERROR [device_type not supported]"
        colored_red(output_err)
        summary_report(output_err)

print("\n")

# connect to the device w/ netmiko
if credentials.get("GIT_TOKEN") != "" and os.path.isdir(".git"):
    print("Pushing on git repo...")
    git_push(repo, commit_message)
else:
    pass
