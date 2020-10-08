import requests
import time
import json
import sys
"""
get the seed player name

Challenger: Revenge.   HJ973T8HuosElWY06Wxv1Pet2Gg_f12U5LREWOO0_mAARXY
Grandmaster: NoNoYogi. 2nQifvh00zEC1gAIPGvV5cgzfF_R2D9BcI-d7Je9ZHiR5w
Diamond: Abeling.      rMWskjT8OONg0URxHCrusVh0fB01bOnG97hVuSrjIBrkQEg
Platinum: Zhou.        fMO0wQ7D6gVGpr1Jxr8eBYafmYu778Dk7jRUW8i-oxMMEQ
Gold: IceStorm.         bPuu2oPBaKhccwOS01_hk4yoSWxMvDKBvbkyIkbsvPtuxTM
Bronze: Original.      iqX1iW29iNYy-SoEq3oepsbl-fRh-L8Qw9LZ2ISdmgImyg
Silver: charlice.      yyRCWIDrzev_b4uoyPS-9fMTt_zcc15Nts1mNKYQnaK1k9s
Unrank: Zhang.         rBtvvQYDWmtjVuPuDLJdi6hK-bYUHjvjxCq-iQociD38k4I
"""


class lolAPi:
    def __init__(self, api_key, url):
        with open(r"../data/accountid.csv",'r') as account_f:
            self.lines = [line.strip("\n") for line in account_f.readlines()]
            self.api_key = api_key

            self.matchlist = []
            self.newaccount = []
            # use the firebase to store the result
            self.firebase_url = url
            
    #get the match list
    def getMatchlist(self):
        for accountid in self.lines:

            url_account = f"https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{accountid}?api_key={self.api_key}"

            # requests have a time limitation 200 times for 2 minutes

            r = requests.get(url_account)
            time.sleep(1.5)

            if r.ok:
                #string data
                str_data = r.text
                #transfer data from str to dict
                dict_data = json.loads(str_data)
                for item in dict_data["matches"]:
                    try:
                        self.matchlist.append(item["gameId"])
                    except KeyError:
                        pass
            elif r.status_code == 403:
                #api_key is invalid
                f = open("log.txt","a")
                f.write("invalid key"+" "+url_account+"\n")
                f.close()

                # generate new seed 
                self.write_account()
                sys.exit()
            
            else:
                f = open("log.txt","a")
                f.write("getMatchlist error"+" "+url_account+"\n")
                f.close()
                pass

            self.getMatches()
            self.matchlist = []

    def getMatches(self):

        for matchid in self.matchlist:
            #print(matchid)
            #for requests quto limitation
            #match_content
            url_matches = f"https://na1.api.riotgames.com/lol/match/v4/matches/{matchid}?api_key={self.api_key}"
            #match_timeline
            url_timeline = f"https://na1.api.riotgames.com/lol/match/v4/timelines/by-match/{matchid}?api_key={self.api_key}"
            r_1 = requests.get(url_matches)
            r_2 = requests.get(url_timeline)

            # get the data
            match_content = r_1.text
            match_content = match_content.encode("utf-8")

            match_timeline = r_2.text
            match_timeline = match_timeline.encode("utf-8")

            time.sleep(2)

            #upload to firebase
            if self.firebase_url[-1] == "/":
                firebase_matches = self.firebase_url +f"project/matches/{matchid}.json"
                firebase_timeline = self.firebase_url +f"project/timeline/{matchid}.json"
            else:
                firebase_matches = self.firebase_url +f"/project/{matchid}.json"
                firebase_timeline = self.firebase_url +f"/project/{matchid}.json"

            r_post1 = requests.put(firebase_matches, match_content)
            r_post2 = requests.put(firebase_timeline, match_timeline)

            if r_post1.ok and r_post2.ok:
                json_content = json.loads(match_content)
                #print(json_content.keys())
                try:
                    parts = json_content["participantIdentities"]

                    #parts should be a dict structure

                    for part in parts:
                        account_id = part["player"]["accountId"]
                        self.newaccount.append(account_id)
                except KeyError:
                    pass
            else:
                f = open("log.txt","a")
                f.write("firebases problem\n")
                f.close()

    def write_account(self):
        with open(r"../data/accountid.csv",'w') as account_f:
            for account_id in self.newaccount:
                if account_id not in self.lines:
                    account_f.write(account_id+"\n")

if __name__ == "__main__":
    api_key = sys.argv[1]
    firebase_url = sys.argv[2]
    
    model = lolAPi(api_key, firebase_url)
    model.getMatchlist()
    model.getMatches()
    model.write_account()

