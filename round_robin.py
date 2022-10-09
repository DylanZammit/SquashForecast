from itertools import combinations
from copy import deepcopy
from pprint import pprint as print
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unicodedata import normalize
import requests


# https://stackoverflow.com/questions/24471136/how-to-find-all-paths-between-two-graph-nodes
def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:# or graph[start] == -1:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths       

def score2prob(score):
    return score/5*0.8+0.1

def prob2score(p, r=True):
    if p == 0.5: return 2.5
    out = (p-0.1)*5/0.8
    return round(out) if r else out

def main(table):
    predicted = deepcopy(table)
    teams = table.keys()
    for team1, team2 in combinations(teams, 2):
        probs = []
        if team2 not in table[team1]:
            paths = find_all_paths(table, team1, team2)
            for path in paths:
                for i in range(len(path)):
                    if i == len(path)-1: continue
                    a = path[i]
                    b = path[i+1]
                    p = score2prob(table[a][b])
                    q = p*q/(p*q+(1-p)*(1-q)) if i else p
                probs.append(q)
            p = sum(probs)/len(probs) if len(probs) else 0.5
            predicted[team1][team2] = prob2score(p)
            predicted[team2][team1] = prob2score(1-p)
    return predicted


def clean(x):
    if not isinstance(x, str): return
    return int(x[0])


if __name__ == "__main__":

    url = 'https://www.sportyhq.com/club/box/view/60'
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers=header)
    dfs = pd.read_html(r.text)


    for table in dfs:
        names = [name.split()[1] for name in table.iloc[:,1]]
        table = table.drop(table.columns[[0, 1, -1]], axis=1)
        table.columns = names
        table.index = names
        print(table)
        table = table.applymap(clean).fillna(np.nan).T.to_dict()
        table = {k: {a: int(b) for a, b in v.items() if not np.isnan(b)} for k, v in table.items()}

        pred = main(table)
        standings = {k: sum([score if score < 2.5 else (score+1 if score > 2.6 else score+0.5) for score in v.values()]) for k, v in table.items()}
        
        table_pred = pd.DataFrame(pred).T
        scores_pred = (table_pred.T + (table_pred.T >= 3) + 1).sum()
        table_pred['scores'] = scores_pred
        table_pred = table_pred.sort_values('scores', ascending=False).fillna(-1)#.astype(int)
        table_pred = table_pred[table_pred.index.to_list() + ['scores']]
        print(table_pred)
    
