import os
import requests
import json
import logging

# logging.getLogger("urllib3").setLevel(logging.DEBUG)

def send_message(channel, message):
    try:
        webhook_url = os.environ["SLACK_WEBHOOK_{channel}".format(channel=channel)]
    except KeyError:
        logging.error("No known webhook for channel: {channel} - "
                      "must provide SLACK_CHANNEL_{channel} environment variable.".format(channel=channel))
        raise
    requests.post(webhook_url, json={"text": message})

def slack_api(method, data):
    token = os.environ["SLACK_TOKEN"]
    url = "https://slack.com/api/{method}".format(method=method)
    headers = {"Authorization": "Bearer {t}".format(t=token)}
    logging.debug("headers: {h}".format(h=headers))
    res = requests.post(url, headers=headers, data=data)
    if res.status_code != 200:
        logging.error("Slack API returned status: {status}".format(status=res.status))
        logging.error(res.content)
    return json.loads(res.content)

def slack_users_info(user):
    logging.debug("asking for info for user: {}".format(user))
    return slack_api("users.info", {"user": user, "include_locale": "false"})['user']
