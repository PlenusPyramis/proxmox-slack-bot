import os
import requests
import json
import logging
import hmac
import hashlib

logger = logging.getLogger("slack")
logger.setLevel(logging.DEBUG)

# logging.getLogger("urllib3").setLevel(logging.DEBUG)

class InvalidSlackSignatureException(Exception):
    pass

def api(method, data):
    token = os.environ["SLACK_TOKEN"]
    url = "https://slack.com/api/{method}".format(method=method)
    headers = {"Authorization": "Bearer {t}".format(t=token)}
    logger.debug("headers: {h}".format(h=headers))
    res = requests.post(url, headers=headers, data=data)
    if res.status_code != 200:
        logger.error("Slack API returned status: {status}".format(status=res.status))
        logger.error(res.content)
    return json.loads(res.content)

def verify_signature(signature, timestamp, body, signing_key, version="v0"):
    sig_basestring = "{version}:{timestamp}:{body}".format(
        version=version, timestamp=timestamp, body=body)
    logger.debug("signature: {s}".format(s=signature))
    logger.debug("sig_basestring: {s}".format(s=sig_basestring))
    digest = hmac.new(signing_key.encode("utf-8"),
             msg=sig_basestring.encode("utf-8"),
             digestmod=hashlib.sha256).hexdigest()
    computed_signature = "{version}={digest}".format(version=version, digest=digest)
    logger.debug("computed_signature: {s}".format(s=computed_signature))

    return signature == computed_signature

def send_message(channel, message):
    try:
        webhook_url = os.environ["SLACK_WEBHOOK_{channel}".format(channel=channel)]
    except KeyError:
        logger.error("No known webhook for channel: {channel} - "
                      "must provide SLACK_WEBHOOK_{channel} environment variable.".format(channel=channel))
        raise
    requests.post(webhook_url, json={"text": message})


def users_info(user):
    logger.debug("asking for info for user: {}".format(user))
    return api("users.info", {"user": user, "include_locale": "false"})['user']
