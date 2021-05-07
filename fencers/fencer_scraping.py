import requests
import json
from bs4 import BeautifulSoup


def get_fencer_info_from_ID(fencer_ID, use_cache = True):
    """
    Takes url for athlete page and returns dict of fencer data with keys FENCERS_DF_COLS
    """
    # open cache to read/write fencer data 
    with open('fencer_cache.txt') as fencer_cache:
        cached_data = json.load(fencer_cache)

    # --------------------------------------------------------
    # Check if fencer is in cache (uses potentially old data)
    # --------------------------------------------------------

        


    # --------------------------------------------------------
    # If not cached or using cache, pull fencer data from url
    # --------------------------------------------------------


    fencer_url = "https://fie.org/athletes/"+str(fencer_ID)
    req = requests.get(fencer_url)
    soup = BeautifulSoup(req.content, 'html.parser')

    # h1 class="AthleteHero-fencerName
    name_tag = soup.find('h1', class_='AthleteHero-fencerName')
    fencer_name = name_tag.get_text()

    # window._tabOpponents = [{"date":"2021-04-10",
    #                           "fencer1":{"id":"52027","name":"PARK Faith","nationality":"USA","isWinner":true,"score":"5"},
    #                           "fencer2":{"id":49302,"name":"CARDOSO Elisabete","nationality":"POR","isWinner":false,"score":"2"},"competition":"Championnats du monde juniors-cadets","season":"2021","competitionId":"235","city":"Le Caire"},
    script = next(soup.find('script', id="js-single-athlete").children)
    # each variable window._XXXX is ';' separated and window._tabOpponents contains data that includes fencer nationality
    var_list = script.split(';')
    # get window._tabOpponents Data
    tabOpp_var_name = "window._tabOpponents "
    tabOpp_string = [text.strip() for text in var_list if
                     text.strip().startswith(tabOpp_var_name)][0]
    tabOpp_list = json.loads(tabOpp_string.split(" = ")[1])
    if len(tabOpp_list)>0 and int(tabOpp_list[0]['fencer1']['id']) == fencer_ID:
        nationality = tabOpp_list[0]['fencer1']['nationality']        
    else:
        nationality = ""
    info_div = soup.find('div', class_="ProfileInfo")
   
    weapon = ""
    points = 0
    hand = ""
    age = ""
    rank = ""
    for info_item in info_div.children:
        if(info_item.get_text().startswith('foil') or info_item.get_text().startswith('epee') or info_item.get_text().startswith('sabre')):
            weapon = info_item.get_text()
        elif(info_item.get_text().startswith('Pts')): # second text is either value of points (may be 0) or "-"
            pts_text = list(info_item.children)[1].get_text()
            try:
                points = float(pts_text)
            except ValueError:
                points = 0 
        elif(info_item.get_text().startswith('Hand')):
            hand = list(info_item.children)[1].get_text()
        elif(info_item.get_text().startswith('Age')):
            age = list(info_item.children)[1].get_text()
        elif(info_item.get_text().startswith('Rank')):
            rank = list(info_item.children)[1].get_text()

    # save data to cache for potential future use (even if not drawing from cache)
    return {'id': fencer_ID, 'name': fencer_name, 'nationality': nationality, 'url': fencer_url, 'hand': hand, 'weapon': weapon, 'points': points, 'rank': rank, 'age': age}
