This telegram bot is utilised for the election season (kähmykausi) of Inkubio.

How to use:

1. Create a config.py file and fill it with the required information (example)
   1. bot_token = "your_token" 
      1. Get this from BotFather
   2. group_ids = ["id1", "id2"]
      1. You can get these for example by adding @getidsbot to the chats
      2. But also other ways to obtain this
   3. forum_url = "https://yourforum.com/"


2. Configure the Discourse forum webhook settings
   1. Your forum -> Additional settings -> Webhooks -> Create
   2. URL where your code is working (local server or hosted somewhere)
   3. Content type: apllication/json
   4. Select triggering events (creation of topics and posts for this)
   5. Select in which discussion areas these events trigger can happen
   6. Tick "Active"
   7. Should be working now


3. Check the category_id's so you can determine which message to send (toimari/hallitus)
4. Run the kahmy_bot.py file.
5. Wait for someone to make a post to your forum and enjoy.
6. The messages contain a link to the topic in question for easy access from the chat

Bot is developed using Python version 3.12 and needed packages for run the project are flask and requests.

To help with the usage it is also recommended to tap from the forum API settings "retry web hook events". This ensures that if the messaging to the chat fails, the forum will try to push an update again (in 1, 5, 25 and 125 minutes) until successfull.
This way even if something breaks, every message should get through and as a last resort from the logs, you can manually push individual events again.
