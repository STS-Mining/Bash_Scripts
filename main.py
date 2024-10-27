# Author - STS Mining | Steve

''' Be sure to add your discord webhook down below '''

import json
import requests

server_names_rpc_hosts = {
    "USA": {
        "RPC_HOST": "http://",
        "FOLDER_LOCATION": "path-to-where-you-want-to-save-the-json-files",
    },
    "Europe": {
        "RPC_HOST": "http://",
        "FOLDER_LOCATION": "path-to-where-you-want-to-save-the-json-files",
    },
}

coins = [
    {
        "COIN_NAME": "Radiant",
        "COIN_SYMBOL": "RXD",
        "RPC_USER": "",
        "RPC_PASSWORD": "",
        "RPC_PORT": 0,
        "NETWORK_BLOCKHEIGHT": "https://www.zpool.ca/api/currencies",
        "TIME_RUNNING_ENABLED": True,
    },
    # {
    #     "COIN_NAME": "",
    #     "COIN_SYMBOL": "",
    #     "RPC_USER": "",
    #     "RPC_PASSWORD": "",
    #     "RPC_PORT": 0,
    #     "NETWORK_BLOCKHEIGHT": "",
    #     "TIME_RUNNING_ENABLED": True,
    # },
]

def convert_blocktime(sec):
    weeks = sec // (7 * 24 * 3600)
    sec %= (7 * 24 * 3600)
    days = sec // (24 * 3600)
    sec %= (24 * 3600)
    hours = sec // 3600
    sec %= 3600
    minutes = sec // 60
    sec %= 60
    time_str = ""
    if weeks:
        time_str += "%dw " % weeks
    if days:
        time_str += "%dd " % days
    if hours:
        time_str += "%dh " % hours
    if minutes:
        time_str += "%dm " % minutes
    if sec:
        time_str += "%ds" % sec

    return time_str.strip()

def json_rpc_call(server_details, coin, method, params):
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        f"{server_details['RPC_HOST']}:{coin['RPC_PORT']}",
        auth=(coin['RPC_USER'], coin['RPC_PASSWORD']),
        headers=headers,
        data=json.dumps(payload),
    )
    if response.status_code != 200:
        raise Exception(
            "JSON-RPC call failed with status code: {}".format(response.status_code))
    response_json = response.json()
    if "error" in response_json and response_json["error"] is not None:
        raise Exception(
            "JSON-RPC call returned error: {}".format(response_json["error"]))
    return response_json["result"]


def send_discord_notification(server_name, coin_name):
    ##################################################
    discord_webhook = "ADD-YOUR-DISCORD-WEBHOOK-HERE"

    data = {
        "content": "",
        "username": "Daemon Offline Alert",
        "type": "rich"
    }
    data["embeds"] = [
        {
            "title": "❌ {} Daemon is Offline ... ❌\n\n".format(server_name) + coin_name,
            "color": 16739860,
            "image": {},
            "thumbnail": {},
        }
    ]
    requests.post(discord_webhook, json=data)


def send_discord_sync(server_name, coin_name):
    #################################################
    discord_webhook = "ADD-YOUR-DISCORD-WEBHOOK-HERE"

    data = {
        "content": "",
        "username": "Daemon Syncing Alert",
        "type": "rich"
    }
    data["embeds"] = [
        {
            "title": "❌ {} Daemon is out of sync ... ❌\n\n".format(server_name) + coin_name + "\n\n{}".format(network_sync_status),
            "color": 16739860,
            "image": {},
            "thumbnail": {},
        }
    ]
    requests.post(discord_webhook, json=data)

for server_name, details in server_names_rpc_hosts.items():
    folder_location = details["FOLDER_LOCATION"]
    rpc_host = details["RPC_HOST"]

    for coin in coins:
        try:
            blockheight = json_rpc_call(details, coin, "getblockcount", [])

            if coin.get("TIME_RUNNING_ENABLED", False):
                time_running = json_rpc_call(details, coin, "uptime", [])
                coin["time_running"] = convert_blocktime(
                    time_running) if time_running else "N/A"
            else:
                coin["time_running"] = "N/A"

            ##################################################
            ###### Be sure to add all coin symbols here ######
            ##################################################
            if coin["COIN_SYMBOL"] in ["RXD",]:
                network_blockheight_url = coin.get("NETWORK_BLOCKHEIGHT")
                response_network_blockheight = requests.get(
                    network_blockheight_url)
                if response_network_blockheight.status_code == 200:
                    network_blockheight_data = json.loads(
                        response_network_blockheight.text)
                    network_blockheight = network_blockheight_data[coin["COIN_SYMBOL"]]["height"]
                else:
                    print(
                        f"Failed to download JSON data from Network BlockHeight URL for {coin['COIN_NAME']}")
                    continue
            else:
                network_blockheight_url = coin.get("NETWORK_BLOCKHEIGHT")
                if network_blockheight_url:
                    response_network_blockheight = requests.get(
                        network_blockheight_url)
                    if response_network_blockheight.status_code == 200:
                        network_blockheight = json.loads(
                            response_network_blockheight.text)
                    else:
                        print(
                            f"Failed to download JSON data from Network BlockHeight URL for {coin['COIN_NAME']}")
                        continue
                else:
                    print(f"No NETWORK_BLOCKHEIGHT for {coin['COIN_NAME']}")
                    continue

            sync_difference = blockheight - network_blockheight
            sync_percentage = 100.0 - \
                abs(sync_difference / network_blockheight) * 100
            status_icon = "✅" if sync_difference > -10 else "❌"
            sync_status = f"{sync_difference} block(s) {'behind' if sync_difference < 0 else 'ahead'}"
            percentage_status = f"{sync_percentage:.2f}%"
            network_sync_status = f"{status_icon} {percentage_status}"
            if sync_percentage < 90:
                send_discord_sync(coin["COIN_NAME"])
                print(f"{coin['COIN_NAME']} Sending to discord...")
            print(f"{coin['COIN_NAME']}, {network_sync_status}")

            coin_data = {
                "server_name": server_name,
                "coin_name": coin["COIN_NAME"],
                "coin_symbol": coin["COIN_SYMBOL"],
                "daemon_blockheight": blockheight,
                "network_blockheight": network_blockheight,
                "sync_difference": sync_status,
                "network_sync": network_sync_status,
                "time_running": convert_blocktime(time_running),
            }

            if server_name:
                folder_location = details["FOLDER_LOCATION"]  # Correct folder location
                file_path = f"{folder_location}/{coin['COIN_NAME']}.json"

                with open(file_path, "w") as outfile:
                    json.dump(coin_data, outfile, indent=4)
            else:
                print("Server information not found for the coin.")

        except Exception as e:
            print(f"Error while processing {coin['COIN_NAME']}: {str(e)}")

            coin_data = {
                "server_name": server_name,
                "coin_name": coin["COIN_NAME"],
                "coin_symbol": coin["COIN_SYMBOL"],
                "daemon_blockheight": "❌",
                "network_blockheight": "❌",
                "sync_difference": "❌",
                "network_sync": "❌",
                "time_running": "❌ Daemon Offline",
            }

            if server_name:
                folder_location = details["FOLDER_LOCATION"]
                file_path = f"{folder_location}/{coin['COIN_NAME']}.json"

                with open(file_path, "w") as outfile:
                    json.dump(coin_data, outfile, indent=4)
            else:
                print("Server information not found for the coin.")
            send_discord_notification(coin["COIN_NAME"], server_name)
            continue