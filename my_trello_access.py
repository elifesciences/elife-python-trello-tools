import os
from trello import TrelloClient
import re 
from collections import defaultdict
import csv 

trello_key = os.environ['TRELLO_API_KEY']
trello_secret = os.environ['TRELLO_API_SECRET']
trello_oauth_token = os.environ['TRELLO_OAUTH_TOKEN']
trello_oauth_secret = os.environ['TRELLO_OAUTH_SECRET']

client = TrelloClient(
	api_key=trello_key,
	api_secret=trello_secret,
	token=trello_oauth_token,
	token_secret=trello_oauth_secret
)

card_labels = {}

def get_boards(client):
	boards = client.list_boards()
	return boards  

def get_sprint_boards(boards):
	sprint_boards = []
	for board in boards:
		if board.name[0:6] == "sprint":
			sprint_boards.append(board)
	return sprint_boards

def select_a_sprint(sprint_boards):
	index = 1
	print "select a sprint> "
	for board in sprint_boards:
		print index, " :",  board.name
		index += 1 
	index = raw_input("selection = ")
	print "you have selected", sprint_boards[int(index) - 1].name  
	return sprint_boards[int(index) - 1]

def get_cards_from_board(board):
	cards = board.get_cards()
	for card in cards:
		card.fetch()
	return cards 

def get_card_titles(cards):
	card_titles = []
	for card in cards:
		print card.name 

def get_estimate_from_title(title):
	p = re.compile('\((.*)\)')
	if p.search(title):
		estimate = p.search(title).group().rstrip(")").lstrip("(")
	else:
		estimate = 0.0 
	return float(estimate) 

def get_effort_from_title(title):
	p = re.compile('\[(.*)\]')
	if p.search(title):
		effort = p.search(title).group().rstrip("]").lstrip("[")
	else:
		effort = 0.0	
	return float(effort)  

def get_labels_from_card(card):
	labels = card.labels
	return labels

def check_card_against_category(card, category):
	labels = card.labels
	p = re.compile(category)
	for label in labels:
		label_name = label["name"]
		if p.search(label_name):
			return True
	return False 

def sum_effort_estimate(cards):
	total_estimates = 0.0
	total_effort = 0.0

	for card in cards:
		card_estimate = get_estimate_from_title(card.name)
		card_effort = get_effort_from_title(card.name)

		total_estimates += card_estimate
		total_effort += card_effort 

	return (total_estimates, total_effort)

def sum_project_categories(cards, categories):
	category_estimates = defaultdict(float)
	for card in cards:
		card_estimate = get_estimate_from_title(card.name)
		card_effort = get_effort_from_title(card.name)

		for category in categories:
			if check_card_against_category(card, category):
				category_estimates[category + "_estimate"] += card_estimate
				category_estimates[category + "_effort"] += card_effort

	return category_estimates 

def f_as_p(value):
	"""
	takes a float and formats as a % 
	"""
	percent = str(value).split(".")[1]
	if percent == "0" and str(value).split(".")[0] == "1":
		percent = "100%"
	elif percent == "0" and str(value).split(".")[0] == "0":
		percent = "0%"
	else:
		percent = str(percent[0:2]) + "%"
	return percent

def get_done_cards_from_board(sprint, all_cards):
	lists = sprint.all_lists()
	done_lists = []
	done_cards = []
	p = re.compile("done", re.IGNORECASE)
	for l in lists:
		if p.search(l.name):
			done_lists.append(l)
	if done_lists:
		for l in done_lists:
			list_cards = l.list_cards()
			done_cards.extend(list_cards)

	# this is a premature optimisation, we have already called a card.fetch()
	# funciton eariler, which was noted to be an expensive operaion timewise
	# so here we pass in those cards and filter on id to explicitly 
	# avoid doing a card.fetch() operation on the cards we have dervived from the
	# done lists. 
	return_cards = []
	done_cards_ids = []
	for card in done_cards: done_cards_ids.append(card.id)

	for card in all_cards:
		if card.id in done_cards_ids:
			return_cards.append(card)

	return return_cards

def print_report_row(estimate_value, total_estimate, effort_vlaue, total_effort, dev_day):
	report_row = gen_csv_report_row(estimate_value, 
									total_estimate, 
									effort_vlaue, 
									total_effort, dev_day)
	for item in report_row: print item, 

def gen_csv_report_row(estimate_value, total_estimate, effort_vlaue, total_effort, dev_day):
	csv_report_row = [ estimate_value, f_as_p(estimate_value / total_estimate), 
						round(estimate_value / dev_days, 2), effort_vlaue, 
						f_as_p(effort_vlaue / total_effort),  
						round(effort_vlaue / dev_days, 2)
						]
	return csv_report_row

def print_report(sprint_name, categories, dev_days, estimate, effort, category_work, done_estimate, done_effort, done_category_work):
	# TODO: function naming in this function is terrible - refactor 
	print ""
	print "report for: ", sprint_name
	print "total estimated effort = ",  estimate 
	print "effort elapsed to date = ", effort  

	print ""
	print "totals: ", 
	print_report_row(estimate, estimate, effort, effort, dev_days)
	print_report_row(done_estimate, done_estimate, done_effort, done_effort, dev_days)
	print "\n" 

	for category in categories:
		try:
			category_estimate = category_work[category + "_estimate"]
		except:
			category_estimate = 0.0
		try:
			category_effort = category_work[category + "_effort"]
		except:
			category_effort = 0.0
		try: 
			done_category_estimate = done_category_work[category + "_estimate"]
		except:
			done_category_estimate = 0.0 
		try:
			done_category_effort = done_category_work[category + "_effort"]
		except:
			done_category_effort = 0.0

		print category, ": ",
		print_report_row(category_estimate, estimate, category_effort, effort, dev_days)
		print_report_row(done_category_estimate, done_estimate, done_category_effort, done_effort, dev_days)
		print "\n"

def report_to_csv(sprint_name, categories, dev_days, estimate, effort, category_work, done_estimate, done_effort, done_category_work):
	csvfile = open("trello_report.csv","wb")
	report_writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL) 

	report_writer.writerow(["report for: " + sprint_name])
	report_writer.writerow(["total estimated effort = " + str(estimate)]) 
	report_writer.writerow(["effort elapsed to date = " + str(effort)])  

	col_headings = ["category",	
					"estimate",	
					"% of total estimate",	
					"estimate per per dev day",	
					"effort",	
					"% of total effort",	
					"effort per dev", 
					"done estimate",
					"% of total done estimate",	
					"done estimate per dev day",	
					"done effort", 	
					"% of total done effort",	
					"done points per dev day"]

	report_writer.writerow(col_headings)  				
	report_row = ["totals"]
	report_row.extend(gen_csv_report_row(estimate, estimate, effort, effort, dev_days))
	report_row.extend(gen_csv_report_row(done_estimate, done_estimate, done_effort, done_effort, dev_days))
	report_writer.writerow(report_row)  

	for category in categories:
		try:
			category_estimate = category_work[category + "_estimate"]
		except:
			category_estimate = 0.0
		try:
			category_effort = category_work[category + "_effort"]
		except:
			category_effort = 0.0
		try: 
			done_category_estimate = done_category_work[category + "_estimate"]
		except:
			done_category_estimate = 0.0 
		try:
			done_category_effort = done_category_work[category + "_effort"]
		except:
			done_category_effort = 0.0

		report_row = [category]
		report_row.extend(gen_csv_report_row(category_estimate, estimate, category_effort, effort, dev_days))
		report_row.extend(gen_csv_report_row(done_category_estimate, done_estimate, done_category_effort, done_effort, dev_days))

		report_writer.writerow(report_row)  


def get_cards_in_done_state(cards):
	return None 

if __name__ == "__main__":
	categories = ["enhancement", "bugfix", "infrastructure", "new development"]

	boards = get_boards(client)
	sprint_boards = get_sprint_boards(boards)
	sprint = select_a_sprint(sprint_boards)
	sprint_name = sprint.name
	cards = get_cards_from_board(sprint)
	done_cards = get_done_cards_from_board(sprint, cards)

	estimate, effort = sum_effort_estimate(cards)
	done_estimate, done_effort = sum_effort_estimate(done_cards)
	
	category_work = sum_project_categories(cards, categories)	
	done_category_work = sum_project_categories(done_cards, categories)	

	dev_days = 27.0 # TODO: need to extract this from a trello card 
	print_report(sprint_name, categories, dev_days, estimate, effort, category_work, done_estimate, done_effort, done_category_work)
	report_to_csv(sprint_name, categories, dev_days, estimate, effort, category_work, done_estimate, done_effort, done_category_work)




