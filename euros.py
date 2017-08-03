import pandas, time
from datetime import datetime, timedelta
from selenium import webdriver

def main():
	teams, scores = get_final_scores()
	score_table = read_guess_scores('euros.csv')
	points = []
	for row in score_table.itertuples():
		date_string = '{date}-2016 {time}'.format(date=row.Date, time=row.Time)
		match_time = datetime.strptime(date_string, '%d-%b-%Y %H:%M')
		if datetime.now()+timedelta(hours=6) >= match_time:
			guess_tuple = ((row.Country, row._8), (row.Score, row._7))
			final_tuple = (teams[row.Index - 1], scores[row.Index - 1])
			points.append(check_score(guess_tuple, final_tuple))
	

def check_score(guess, final):

	if guess[0] != final[0]:
		return 'Error! {guess_teams} is not {final_teams}!'.format(guess_teams=guess[0], final_teams=final[0])
	else:
		guess_diff = guess[1][0] - guess[1][1]
		final_diff = final[1][0] - final[1][1]
		if guess_diff == 0 or final_diff == 0:
			if guess_diff == 0 and final_diff == 0:
				is_correct_winner = True
			else:
				is_correct_winner = False
		else:
			if (guess_diff > 0) == (final_diff > 0):
				is_correct_winner = True
			else:
				is_correct_winner = False
		is_correct_diff = guess_diff == final_diff
		is_correct_score = (guess[1][0] == final[1][0]) and (guess[1][1] == final[1][1])
		return 25 * ((2 * is_correct_winner) + is_correct_diff + is_correct_score)

def get_final_scores():
	''' Collects final scores from Euro 2016 website and returns them in a Pandas DataFrame. '''
	driver = webdriver.PhantomJS('/phantomjs-2.1.1-windows/bin/phantomjs.exe') # PhantomJS path - as set, file MUST be in same folder as script
	teams = []
	scores = []
	for i in [1, 2, 3]:
		driver.get('http://www.uefa.com/uefaeuro/season=2016/matches/index.html#md/{}'.format(i))
		time.sleep(2)
		teams  += [team.get_attribute('innerHTML') for team in driver.find_elements_by_xpath('//span[@class="team-name_name"]')]
		scores += [int(score.get_attribute('innerHTML')) for score in driver.find_elements_by_xpath('//span[@class="js-team--home-score" or @class="js-team--away-score"]')]
	driver.close()
	teams = list(zip(teams[0::2], teams[1::2]))
	scores = list(zip(scores[0::2], scores[1::2]))
	final_table = pandas.DataFrame({"Team 1": [x[0] for x in teams], "Score 1": [x[0] for x in scores], "Score 2": [x[1] for x in scores], "Team 2": [x[1] for x in teams]}, index=list(range(1, len(teams) + 1)), columns=['Team 1', 'Score 1', 'Score 2', 'Team 2'])
	return final_table

def read_guess_scores(filename):
	score_table = pandas.read_csv(filename, header=10, nrows=37, usecols=[3,4,5,6,7,9,11,13,17]).ix[1:]
	score_table.rename(columns={'Unnamed: 11': 'Score.1'}, inplace=True)
	dates = []
	return score_table

def show_team_matches(team, final_scores):
	return final_scores[final_scores['Team 1'] == team].append(final_scores[final_scores['Team 2'] == team])

if __name__ == '__main__':
	main()