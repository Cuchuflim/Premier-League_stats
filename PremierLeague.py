from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ChromeOptions
import pandas as pd
import time
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import datetime

def init_driver():
    options = ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver

def get_element(driver, by, value, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def wait_for_text_change(driver, element, timeout=20):
    initial_text = element.text
    WebDriverWait(driver, timeout).until(lambda d: element.text != initial_text)
    return element.text

def extract_team_stats(driver, team, season_id):
    url = f'https://www.premierleague.com/clubs/{team["id"]}/{team["name"]}/stats?se={season_id}'
    driver.get(url)
    print(f"Getting {url}...")

    elements = {
        "Matches_Played": (By.CSS_SELECTOR, "span[data-stat='wins,draws,losses']"),
        "Wins": (By.CSS_SELECTOR, "span[data-stat='wins']"),
        "Losses": (By.CSS_SELECTOR, "span[data-stat='losses']"),
        "Goals": (By.CSS_SELECTOR, "span[data-stat='goals']"),
        "Goal_Conceded": (By.XPATH, "//*[@id='mainContent']/div[3]/div/div/ul/li[3]/div/div[3]/span[2]/span"),
        "Clean_Sheet": (By.CSS_SELECTOR, "span[data-stat='clean_sheet']"),
        "GoalsPerMatch": (By.CSS_SELECTOR, "span[class='allStatContainer js-all-stat-container statgoals_per_game']"),
        "Shots": (By.CSS_SELECTOR, "span[data-stat='total_scoring_att']"),
        "ShotsOnTarget": (By.CSS_SELECTOR, "span[data-stat='ontarget_scoring_att']"),
        "ShootingAccuracy": (By.CSS_SELECTOR, "span[class='allStatContainer js-all-stat-container statshot_accuracy']"),
        "PenaltiesScored": (By.CSS_SELECTOR, "span[data-stat='att_pen_goal']"),
        "BigChancesCreated": (By.CSS_SELECTOR, "span[data-stat='big_chance_created']"),
        "HitWoodwork": (By.CSS_SELECTOR, "span[data-stat='hit_woodwork']"),
        "Passes": (By.CSS_SELECTOR, "span[data-stat='total_pass']"),
        "PassesPerMatch": (By.CSS_SELECTOR, "span[class='allStatContainer js-all-stat-container stattotal_pass_per_game']"),
        "PassAccuracy": (By.CSS_SELECTOR, "span[data-stat='accurate_pass']"),
        "Crosses": (By.CSS_SELECTOR, "span[data-stat='total_cross']"),
        "CrossAccuracy": (By.CSS_SELECTOR, "span[data-stat='accurate_cross']"),
        "GoalsConcededPerMatch": (By.XPATH, "//*[@id='mainContent']/div[3]/div/div/ul/li[3]/div/div[4]/span[2]/span"),
        "Saves": (By.CSS_SELECTOR, "span[data-stat='saves']"),
        "Tackles": (By.CSS_SELECTOR, "span[data-stat='total_tackle']"),
        "TacklesSuccess": (By.CSS_SELECTOR, "span[data-stat='won_tackle']"),
        "BlockedShots": (By.CSS_SELECTOR, "span[data-stat='blocked_scoring_att']"),
        "Interceptions": (By.CSS_SELECTOR, "span[data-stat='interception']"),
        "Clearances": (By.CSS_SELECTOR, "span[data-stat='total_clearance']"),
        "HeadedClearance": (By.CSS_SELECTOR, "span[data-stat='effective_head_clearance']"),
        "AerialBattleDuelsWon": (By.CSS_SELECTOR, "span[data-stat='aerial_won,duel_won']"),
        "ErrorLeadingToGoal": (By.CSS_SELECTOR, "span[data-stat='error_lead_to_goal']"),
        "OwnGoals": (By.CSS_SELECTOR, "span[data-stat='own_goals']"),
        "YellowCards": (By.CSS_SELECTOR, "span[data-stat='total_yel_card']"),
        "RedCards": (By.CSS_SELECTOR, "span[data-stat='total_red_card']"),
        "Fouls": (By.CSS_SELECTOR, "span[data-stat='attempted_tackle_foul']"),
        "Offsides": (By.CSS_SELECTOR, "span[data-stat='total_offside']"),
        "Season": (By.XPATH, "//div[@aria-labelledby='dd-compSeasons']")
    }

    data = {}
    for key, loc in elements.items():
        element = get_element(driver, *loc)
        data[key] = element.text if key != "Matches_Played" else wait_for_text_change(driver, element)

    return data

def extract_team_overview(driver, team):
    url = f'https://www.premierleague.com/clubs/{team["id"]}/{team["name"]}/overview'
    driver.get(url)
    print(f"Getting {url}...")

    elements = {
        "ClubBadge": (By.XPATH, '//*[@id="mainContent"]/header/div[1]/img'),
        "HomeKit": (By.XPATH, '//*[@id="mainContent"]/div[3]/div/div/article[1]/a/picture/img'),
        "AwayKit": (By.XPATH, '//*[@id="mainContent"]/div[3]/div/div/article[2]/a/picture/img'),
        "ThirdKit": (By.XPATH, '//*[@id="mainContent"]/div[3]/div/div/article[3]/a/picture/img')
    }

    data = {}
    data = {key: get_element(driver, *loc).get_attribute("src") for key, loc in elements.items()}
    data["Team_ID"] = team["id"]
    data["TeamName"] = team["name"]
    return data

def upload_to_azure(container_name, file_path, blob_name):
    # Function to upload files to Azure Blob Storage
    connect_str = "Connection string"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

def main():
    print('Beginning...')
    startTime = time.time()
    # Get the current timestamp
    timestamp = datetime.now().timestamp()
    timedt = datetime.fromtimestamp(timestamp)
    formatted_date = timedt.strftime('%Y-%m-%d')

    teams = [
{
        "name": "Arsenal",
        "id": "1",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Chelsea",
        "id": "4",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Aston-Villa",
        "id": "2",
        "id_season": ["578","489","418","363","274","42","27"],
    },
    {
        "name": "Bournemouth",
        "id": "127",
        "id_season": ["578","489","274","210","79","54","42"]
    },
    {
        "name": "Brentford",
        "id": "130",
        "id_season": ["578","489","418"]
    },
    {
        "name": "Brighton-and-Hove-Albion",
        "id": "131",
        "id_season": ["578","489","418","363","274","210","79"]
    },
    {
        "name": "Burnley",
        "id": "43",
        "id_season": ["578","418","363","274","210","79","54","27"]
    },
    {
        "name": "Crystal-Palace",
        "id": "6",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Everton",
        "id": "7",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Fulham",
        "id": "34",
        "id_season": ["578","489","363","210"]
    },
    {
        "name": "Liverpool",
        "id": "10",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Luton-Town",
        "id": "163",
        "id_season": ["578"]
    },
    {
        "name": "Manchester-City",
        "id": "11",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Manchester-United",
        "id": "12",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Newcastle-United",
        "id": "23",
        "id_season": ["578","489","418","363","274","210","79","42","27"]
    },
    {
        "name": "Nottingham-Forest",
        "id": "15",
        "id_season": ["578","489"]
    },
    {
        "name": "Sheffield-United",
        "id": "18",
        "id_season": ["578","363","274"]
    },
    {
        "name": "Tottenham-Hotspur",
        "id": "21",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "West-Ham-United",
        "id": "25",
        "id_season": ["578","489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Wolverhampton-Wanderers",
        "id": "38",
        "id_season": ["578","489","418","363","274","210"]
    },
    {
        "name": "Leicester-City",
        "id": "26",
        "id_season": ["489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Leeds-United",
        "id": "9",
        "id_season": ["489","418","363"]
    },
    {
        "name": "Southampton",
        "id": "20",
        "id_season": ["489","418","363","274","210","79","54","42","27"]
    },
    {
        "name": "Watford",
        "id": "33",
        "id_season": ["418","274","210","79","54"]
    },
    {
        "name": "Norwich-City",
        "id": "14",
        "id_season": ["418","274","42"]
    },
    {
        "name": "West-Bromwich-Albion",
        "id": "36",
        "id_season": ["363","79","54","42","27"]
    },
    {
        "name": "Cardiff-City",
        "id": "46",
        "id_season": ["210"]
    },
    {
        "name": "Huddersfield-Town",
        "id": "159",
        "id_season": ["210","79"]
    },
    {
        "name": "Swansea-City",
        "id": "45",
        "id_season": ["79","54","42","27"]
    },
    {
        "name": "Stoke-City",
        "id": "42",
        "id_season": ["79","54","42","27"]
    },
    {
        "name": "Hull-City",
        "id": "41",
        "id_season": ["54","27"]
    },
    {
        "name": "Middlesbrough",
        "id": "13",
        "id_season": ["54"]
    },
    {
        "name": "Sunderland",
        "id": "29",
        "id_season": ["54","42","27"]
    }
    ]

    driver = init_driver()

    stats = []
    attack = []
    defence = []
    discipline = []
    teamPlay = []
    teamInfo = []

    try:
        for team in teams:
            for season_id in team["id_season"]:
                team_stats = extract_team_stats(driver, team, season_id)
                stats.append({
                    "Team_ID": team["id"],
                    "TeamName": team["name"],
                    "Season": team_stats["Season"],
                    "Matches_Played": team_stats["Matches_Played"],
                    "Wins": team_stats["Wins"],
                    "Losses": team_stats["Losses"],
                    "Goals": team_stats["Goals"],
                    "Goal_Conceded": team_stats["Goal_Conceded"],
                    "Clean_Sheet": team_stats["Clean_Sheet"]
                })
                attack.append({
                    "Team_ID": team["id"],
                    "Season": team_stats["Season"],
                    "Goals": team_stats["Goals"],
                    "GoalsPerMatch": team_stats["GoalsPerMatch"],
                    "Shots": team_stats["Shots"],
                    "ShotsOnTarget": team_stats["ShotsOnTarget"],
                    "ShootingAccuracy%": team_stats["ShootingAccuracy"],
                    "PenaltiesScored": team_stats["PenaltiesScored"],
                    "BigChancesCreated": team_stats["BigChancesCreated"],
                    "HitWoodwork": team_stats["HitWoodwork"]
                })
                teamPlay.append({
                    "Team_ID": team["id"],
                    "Season": team_stats["Season"],
                    "Passes": team_stats["Passes"],
                    "PassesPerMatch": team_stats["PassesPerMatch"],
                    "PassAccuracy%": team_stats["PassAccuracy"],
                    "Crosses": team_stats["Crosses"],
                    "CrossAccuracy%": team_stats["CrossAccuracy"]
                })
                defence.append({
                    "Team_ID": team["id"],
                    "Season": team_stats["Season"],
                    "CleanSheets": team_stats["Clean_Sheet"],
                    "GoalConceded": team_stats["Goal_Conceded"],
                    "GoalsConcededPerMatch": team_stats["GoalsConcededPerMatch"],
                    "Saves": team_stats["Saves"],
                    "Tackle": team_stats["Tackles"],
                    "TackleSuccess%": team_stats["TacklesSuccess"],
                    "BlockedShots": team_stats["BlockedShots"],
                    "Interceptions": team_stats["Interceptions"],
                    "Clearances": team_stats["Clearances"],
                    "HeadedClearance": team_stats["HeadedClearance"],
                    "AerialBattle/DuelsWon": team_stats["AerialBattleDuelsWon"],
                    "ErrorsLeadingToGoal": team_stats["ErrorLeadingToGoal"],
                    "OwnGoals": team_stats["OwnGoals"]
                })
                discipline.append({
                    "Team_ID": team["id"],
                    "Season": team_stats["Season"],
                    "YellowCards": team_stats["YellowCards"],
                    "RedCards": team_stats["RedCards"],
                    "Fouls": team_stats["Fouls"],
                    "Offsides": team_stats["Offsides"]
                })

            team_info = extract_team_overview(driver, team)
            teamInfo.append(team_info)

        # Save the collected data to CSV files
        stats_file = f"teams_stats_{formatted_date}.csv"
        attack_file = f"teams_attack_{formatted_date}.csv"
        team_play_file = f"teams_teamPlay_{formatted_date}.csv"
        defence_file = f"teams_defence_{formatted_date}.csv"
        discipline_file = f"teams_discipline_{formatted_date}.csv"
        team_info_file = f"teams_overview_{formatted_date}.csv"

        # Save the collected data to CSV files
        pd.DataFrame(stats).to_csv(f"teams_stats_{formatted_date}.csv", index=False)
        pd.DataFrame(attack).to_csv(f"teams_attack_{formatted_date}.csv", index=False)
        pd.DataFrame(teamPlay).to_csv(f"teams_teamPlay_{formatted_date}.csv", index=False)
        pd.DataFrame(defence).to_csv(f"teams_defence_{formatted_date}.csv", index=False)
        pd.DataFrame(discipline).to_csv(f"teams_discipline_{formatted_date}.csv", index=False)
        pd.DataFrame(teamInfo).to_csv(f"teams_overview_{formatted_date}.csv", index=False)

        # Upload files to Azure Blob Storage
    
        upload_to_azure("container", stats_file, stats_file)
        upload_to_azure("container", attack_file, attack_file)
        upload_to_azure("container", team_play_file, team_play_file)
        upload_to_azure("container", defence_file, defence_file)
        upload_to_azure("container", discipline_file, discipline_file)
        upload_to_azure("container", team_info_file, team_info_file)

    finally:
        driver.quit()

    print("..End")
    elapsed_time = time.time() - startTime
    minutes, seconds = divmod(elapsed_time, 60)
    print(f'Done in: {int(minutes)} minutes and {seconds:.2f} seconds')

if __name__ == "__main__":
    main()