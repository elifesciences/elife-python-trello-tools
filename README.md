# About

scripts to get data from trello and create reports in google drive

# Requirements 

requires the `py-trello` client.

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


