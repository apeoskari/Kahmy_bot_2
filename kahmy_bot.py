"""
KähmyBot2.0

A telegram bot to be used during Inkubio ry's election season.
The bot sends a notification to specified chats about each application and comments on them.

The bot functions around the forum page's (discourse) webhook, which pushes notifications of certain actions,
which can be specified in the forum settings.
In this case when a new topic or post is created in the forum under certain discussion areas
(again specified in the forum settings)

Questions etc. can be sent to the coder in question:
Aaro Kuusinen
kuusinen.aaro@gmail.com
TG: @apeoskari
"""

from flask import Flask, request, jsonify
import requests

import config

app = Flask(__name__)


def send_message_to_telegram(text, chat_ids):
    """
    Actually sending the message determined in the 'text' parameter to chats specified in 'chat_ids'
    'chat_ids' is a list of the chat ids of chats (groups) you want to send the message to.
    'text' contains the entire message to be sent, including HTML formatting.
    """
    url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Message sent to group {chat_id}")
        else:
            print(
                f"Failed to send message to group {chat_id}. Status code: {response.status_code}"
            )


@app.route("/kahmybot_webhook", methods=["POST"])
def discourse_webhook():
    """Flask route to handle Discourse webhook POST requests"""
    data = request.json
    payload = {}

    HALLITUS_KAHMY_SLUG = "hallitus-kahmyt"
    TOIMARI_KAHMY_SLUG = "toimarikahmyt"

    # Payload
    if "post" in data and data["post"]["category_slug"] in (
        HALLITUS_KAHMY_SLUG,
        TOIMARI_KAHMY_SLUG,
    ):
        payload = data["post"]
        print(payload["category_slug"])
    else:
        return jsonify({"status": "ok"}), 200

    print(payload["category_slug"])
    # Gather all necessary data
    topic_slug = payload["topic_slug"]
    topic_title = payload["topic_title"]
    user_fullname = payload["name"]
    topic_id = payload["topic_id"]
    post_number = payload["post_number"]
    category_slug = payload["category_slug"]

    url = f"{config.forum_url}/t/{topic_slug}/{topic_id}/{post_number}"

    message = ""
    # when post_number == 1 the post is the original post
    post = (post_number, category_slug)
    match post:
        case (1, HALLITUS_KAHMY_SLUG):
            embedded_url = f"<a href='{url}'>hallituskähmy</a>"
            message = f"Uusi {embedded_url} henkilöltä\n<b>{user_fullname}</b>:\n{topic_title}"
        case (1, TOIMARI_KAHMY_SLUG):
            embedded_url = f"<a href='{url}'>toimarikähmy</a>"
            message = f"Uusi {embedded_url} henkilöltä\n<b>{user_fullname}</b>:\n{topic_title}"
        case (post_number, _) if post_number > 1:
            embedded_url = f"<a href='{url}'>kommentti</a>"
            message = f"Uusi {embedded_url} kähmyyn:\n{topic_title}\nhenkilöltä <b>{user_fullname}</b>"

    send_message_to_telegram(message, config.group_ids)

    return jsonify({"status": "ok"}), 200


def create_app():
    return app


if __name__ == "__main__":
    app.run(port=5000, debug=True)
