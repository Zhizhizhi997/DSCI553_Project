import requests
import datetime
import json
import sys

class download:
    def __init__(self, url):

        cur_time = datetime.datetime.now()
        cur_time = cur_time.strftime('%Y-%m-%d %H-%M-%S')
        self.time = cur_time
        self.firebase_url = url
        if self.firebase_url[-1] =="/":
            pass
        else:
            self.firebase_url += "/"
    def matches(self):
        # specify the url to get data from matches
        matches_url = self.firebase_url+"project/matches.json"
        r1 = requests.get(matches_url)
        self.matches_file = self.time + "matches" + ".json"

        with open(self.matches_file,"w") as f:
            json.dump(r1.text, f, indent = 1)

    def timelines(self):
        match_list = []
        # get the match list from matches file
        with open(self.matches_file) as matches_file:
            dict_data = json.load(matches_file)
            # dict_data transfer from string to json
            dict_data = json.loads(dict_data)
            print("total data length:", len(dict_data))

            for item in dict_data:
                data = dict_data[item]
                try:
                    matchid = data["gameId"]
                    match_list.append(matchid)
                except KeyError:
                    pass

        #print(match_list)
        timeline_url =  self.firebase_url+"project/timeline/"

        self.timeline_file = self.time + "timeline" + ".json"
        timelines = open(self.timeline_file, "w")
        add_item = {}
        count = 0
        for matchid in match_list:
            count += 1
            # show the process of code
            print(f"\r {matchid}"+" "+str(count) + "/" + str(len(match_list)), end="")
            r2 = requests.get(timeline_url+str(matchid)+".json")
            add_item[matchid] = json.loads(r2.text)

        # dump dict to json file
        print("dump file to json")
        json.dump(add_item, timelines, indent=1)

        timelines.close()

if __name__ == "__main__":
    url = sys.argv[1]
    model = download(url)
    #generate matches file
    model.matches()
    #generate timeline file
    model.timelines()