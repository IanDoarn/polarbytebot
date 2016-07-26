# Polarbytebot

## Introduction

This is a bot for reddit, meant for doing stuff that I want it to do. Currently this does include posting the content of linked threads from forums/blog posts to the thread they got linked in. It also links posts by tagged game developer employees in to track-subreddits. 

Activated Subreddits for forum posts:

 * /r/Overwatch (and soon related subreddits)
 * /r/Guildwars2
 
Activated Subreddits for blog posts:

 * /r/Guildwars2
 
Developer Tracker:
 
 * /r/Overwatch (and soon related subreddits) -> /r/Blizzwatch
 * /r/Guildwars2 -> /r/gw2devtrack and /r/gw2devtrackalt
 
## Interaction with the bot

You can call the bot to transcript the content of a link with the following notation:

+/u/NAME_OF_YOUR_BOT_ACCOUNT url

Example:

+/u/polarbytebot https://www.guildwars2.com/en/news/out-of-the-shadows-is-live/

Dont forget the + before the username (no space inbetween) and at least one, up to 3 spaces between the username and the url.

To make the bot transcript multiple urls with one post, you need to post this for every url you want to transcript.

## Setup

This code has been made public largely for the purpose of showing what the bot does and how. If you want to run the bot yourself for equal or other purposes compatible with the license feel free to do so.
 
 * requirements.txt includes everything for pip.
 
 * polarbytebot.cfg.example is an example of how your configuration file could look like. Your configuration file should be called polarbytebot.cfg

 * postgres_manage.sh is a shell script to setup the required database and tables, together with a postgres user account. Please change the password before executing.

 * crontab_script.sh is a shell script for running the bot inside a virtualenv using crontab

 * \*_update.\* files are scripts you should run using cron to update program related information (eg. list of ArenaNet employees reddit-accounts)

## More Information

Ask me! /u/Xyooz on reddit!
