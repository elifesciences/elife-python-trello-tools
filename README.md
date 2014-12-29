# About

scripts to get data from trello and create reports in google drive

# Requirements 

requires the `[py-trello](https://github.com/sarumont/py-trello)` client.

# Obtaining tokens for Trello

`py-trello` comes with a `util.py` function for running through the 
authentication process with trello to get a token. You will need
to set you TRELLO_API_KEY and TRELLO_API_SECRET as environemnt
variables first. You can get these two tokens from ...

	$ python trello/uitl.py


# Settings 

set environemnt variables for 

	TRELLO_API_KEY
	TRELLO_API_SECRET
	TRELLO_OAUTH_TOKEN
	TRELLO_OAUTH_SECRET

# TODO

I've created a todo list for this project on the following trello board: 
https://trello.com/b/Uii9iVR4/project-trello-reporting 




- add an extension that can generate burndown charts 
	- add a control to ping a daily update to slack 



