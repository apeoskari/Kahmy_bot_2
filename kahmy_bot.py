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


# Flask route to handle Discourse webhook POST requests
@app.route("/kahmybot_webhook", methods=["POST"])
def discourse_webhook():
    data = request.json
    message = ""

    # Check if the webhook is for a new topic or post
    if "topic" in data:
        # New topic created
        # Get the topic name and the creators name.
        topic_title = data["topic"]["title"]
        name = data["topic"]["created_by"]["name"]

        # format the title and add it to the url so that people can access the topic directly from chat.
        mod_title = str.lower(topic_title).replace(" ", "-")
        url = f"{config.forum_url}t/{mod_title}/{data['topic']['id']}"

        # Specify whether the message is about toimari- or hallituskähmy and hide the url behind that word (HTML format)
        if data["topic"]["category_id"] == 6:
            in_text_url = f"<a href='{url}'>toimarikähmy</a>"
            message = f"Uusi {in_text_url} henkilöltä\n<b>{name}</b>:\n{topic_title}"

        if data["topic"]["category_id"] == 5:
            in_text_url = f"<a href='{url}'>hallituskähmy</a>"
            message = f"Uusi {in_text_url} henkilöltä\n<b>{name}</b>:\n{topic_title}"

        send_message_to_telegram(message, config.group_ids)

    # Check whether a post is an answer to an already existing topic.
    elif "post" in data and data["post"]["post_number"] > 1:
        # New post created
        # Get the topic title and name of the person reacting to it.
        title = data["post"]["topic_slug"]
        name = data["post"]["name"]

        # Again format an url to be added to the message
        mod_title = str.lower(title).replace(" ", "-")
        url = f"{config.forum_url}t/{mod_title}/{data['post']['topic_id']}"
        in_text_url = f"<a href='{url}'>kommentti</a>"

        # Add everything of importance to the message: url, title, sender name.
        message = f"Uusi {in_text_url} kähmyyn:\n{title}\nhenkilöltä <b>{name}</b>"
        send_message_to_telegram(message, config.group_ids)

    return jsonify({"status": "ok"}), 200


def create_app():
    return app


if __name__ == "__main__":
    app.run(port=5000, debug=True)
