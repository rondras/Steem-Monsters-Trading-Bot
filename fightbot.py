
from steem.transactionbuilder import TransactionBuilder
from steembase import operations
from steem import Steem
from steem.blockchain import Blockchain
from steem.account import Account
from steem.post import Post
import json
import datetime
import requests
import time
import requests
import hashlib
import string
import random
from random import randint

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

user = "STEEMUSERNAME"
steem = Steem(nodes=["https://steemd.privex.io"],
          keys=["PRIVATEPOSTINGKEY"])

def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def smfindmatch(json):
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_find_match",
            "json": json,
            "required_auths": [],
            "required_posting_auths": [user],
        }),
    ]
    tb = TransactionBuilder()
    tb.appendOps(ops)
    tb.appendSigner(user, "posting")
    tb.sign()
    tb.broadcast()

def smshowteam(show_json):
    ops = [    
        operations.CustomJson(**{
            "from": user,
            "id": "sm_team_reveal",
            "json": show_json,
            "required_auths": [],
            "required_posting_auths": [user],
        }), 
    ]
    tb = TransactionBuilder()
    tb.appendOps(ops)
    tb.appendSigner(user, "posting")
    tb.sign()
    tb.broadcast()


def match(deckid):
    summoner1 = "C-0X3OXSYUA8" #Selenia Sky 56
    summoner2 = "C-0X3OXSYUA8" #Selenia Sky 56
    summoner3 = "C-0X3OXSYUA8" #Selenia Sky 56
    summoner4 = "C-0X3OXSYUA8" #Selenia Sky 56
    summoner5 = "C-YO2VWID2SW"
    summoner6 = "C-0X3OXSYUA8" #Selenia Sky 56
    summoner7 = "C-YO2VWID2SW" # Tyrus Paladium 38
    summoner8 = "C-0X3OXSYUA8" #Selenia Sky 56
    summoner9 = ""
    summoner10 = ""
    monsters1 = ["C-AZOTS424PC","C-6P55WBF9I8","C-00PPXK0Q8G"] #293332
    monsters2 = ["C-HYCFO8VNFK","C-5J7RYS1QFK","C-T506R4S8IO"] #505752
    monsters3 = ["C-136TZUST6O","C-L810JLD0OG","C-F8TXCLCALC","C-DSJJNNWUXC"] #8149
    monsters4 = ["C-HYCFO8VNFK","C-T506R4S8IO","C-RIW75UV0A8","C-08AVYCGCW0"] #50524657
    monsters5 = ["C-EQTZLJT1ZK","C-C9WDZW485C","C-QW8CYQ44FK","C-RSYVGU0TF4"] #3837423544
    monsters6 =["C-HYCFO8VNFK","C-5J9UIIUZ80","C-T506R4S8IO","C-8J1FFPX4C0","C-RIW75UV0A8"] #5054524651
    monsters7 =["C-EQTZLJT1ZK","C-C9WDZW485C","C-QW8CYQ44FK","C-RSYVGU0TF4"] #37423544
    monsters8 =["C-TIAFKU4DLC","C-QFGL7LOLC0","C-F8TXCLCALC","C-DSJJNNWUXC","C-L810JLD0OG"] #
    monsters9 = []
    monsters10 =[]
    monsters11 =[]

    deck1 = {'summoner': summoner1, 'monsters' : monsters1, 'mana':17} #56293332
    deck2 = {'summoner': summoner2, 'monsters' : monsters2, 'mana':17} #56505752
    deck3 = {'summoner': summoner3, 'monsters' : monsters3, 'mana':17} #568149
    deck4 = {'summoner': summoner4, 'monsters' : monsters4, 'mana':20}
    deck5 = {'summoner': summoner5, 'monsters' : monsters5, 'mana':20}
    deck6 = {'summoner': summoner6, 'monsters' : monsters6, 'mana':20} #565054524651
    deck7 = {'summoner': summoner7, 'monsters' : monsters7, 'mana':20} #3837423544
    deck8 = {'summoner': summoner8, 'monsters' : monsters8, 'mana':20}
    deck9 = {'summoner': summoner9, 'monsters' : monsters9, 'mana':20}
    deck10 = {'summoner': summoner10, 'monsters' : monsters10, 'mana':20}
    deck11 = {'summoner': summoner11, 'monsters' : monsters11, 'mana':20}

    decks = {'1':deck1, '2':deck2, '3':deck3, '4':deck4, '5':deck5, '6':deck6, '7':deck7, '8':deck8, '9':deck9, '10':deck10, '11':deck11}
    decknumber = randint(9, 11)
    deck = decks[str(decknumber)]
    deck = decks[str(deckid)]

    #deck = deck1
    summoner = deck['summoner']
    monsters = deck['monsters']
    mana = deck['mana']

    secret = "YkUGqe9hK0"
    secret = id_generator()
    print (secret)
    strg_to_hash = (summoner + ',' + ",".join(monsters) + ',' + secret)
    hashvalue = hashlib.md5(strg_to_hash.encode('utf-8')).hexdigest()
    print (hashvalue)
    json = '{"match_type":"Ranked","mana_cap":' +str(mana) + ',"team_hash":"' +hashvalue + '","summoner_level":4,"ruleset":"Standard"}'
    print (json)
    # transmit the request to fight
    smfindmatch(json)
    # get the block id for the request to fight
    acc = Account(user)
    check = False
    while (check == False):
        account_history = list(acc.get_account_history(-1, 3, filter_by=["custom_json"]))
        for transaction in account_history:
            custom_json = transaction['json']
            if custom_json == json:
                check = True
                trx_id = transaction['trx_id']
                print (trx_id)
    status = 0
    count = 0
    timeout = False
    while status < 1 and timeout == False:
        count = count +1
        r = requests.get('https://steemmonsters.com/battle/status?id=' +str(trx_id))
        data = r.json()
        status = data['status']
        print ("Waiting for opponent")
        if count > 500:
            timeout = True
    if timeout == False:
        print ("Match found")
        show_json = '{"trx_id":"' + trx_id +'","summoner":"' + summoner + '","monsters":["' +'","'.join(monsters) + '"],"secret":"' +secret +'"}'
        print (show_json)
        smshowteam(show_json)

def run():

    lastblock = steem.head_block_number
    #print (lastblock)
    #print ("Letzter Block in der Blockchain:" +str(lastblock))
    startblock = lastblock -5

    # Ermittele das eigene Rating
    r = requests.get('https://steemmonsters.com/players/details?name=' +str(user))
    data = r.json()
    ratinguser = data['rating']
    print (ratinguser)


    #lade die API
    r = requests.get('https://steemmonsters.com/transactions/history?from_block=' +str(startblock))
    data = r.json()
    for transaction in data:
        transactiontype = transaction['type']
        trx_id = transaction['id']
        #print (trx_id)
        if transactiontype == "sm_find_match":
            r = requests.get('https://steemmonsters.com/battle/status?id=' +str(trx_id))
            data = r.json()
            status = data['status']
            player = data['player']
            #ermittele das Rating des Players
            r = requests.get('https://steemmonsters.com/players/details?name=' +str(player))
            data = r.json()
            ratingplayer = data['rating']
            ratingdelta = abs(ratinguser - ratingplayer)
            #print (status)
            #print (ratingdelta)
            if status == 0 and ratingdelta <500:
                print ("Match found")
                player = transaction['player']
                lastblock = steem.head_block_number
                startblock = lastblock -1000
                r = requests.get('https://steemmonsters.com/transactions/history?from_block=' +str(startblock))
                data = r.json()
                for transaction in reversed(data):
                    if transaction['type'] == "sm_team_reveal":
                        if transaction['player'] == player:
                            #print (transaction) 
                            deckcode =""
                            trxdata =  json.loads(transaction['data'])
                            summoner = trxdata['summoner']
                            monsters = trxdata['monsters']
                            result =  json.loads(transaction['result'])
                            #print (result)
                            r = requests.get('https://steemmonsters.com/cards/find?ids=' +str(summoner))
                            rawdata = r.json()
                            data = rawdata[0]['details']
                            deckcode = str(deckcode) +str(data['id'])
                            #print (data['name'])
                            monsters = trxdata['monsters']
                            for monster in monsters:
                                r = requests.get('https://steemmonsters.com/cards/find?ids=' +str(monster))
                                rawdata = r.json()
                                data = rawdata[0]['details']
                                deckcode = str(deckcode) +str(data['id'])
                                #print (data['name'])
                            print (deckcode)
                            if deckcode == "1621641714":
                                print ("deck suggestion found")
                                deckid = 1
                                match(deckid)
                            if deckcode == "56293332":
                                print ("deck suggestion found")
                                deckid = 3
                                match(deckid)
                            if deckcode == "568149":
                                print ("deck suggestion found")
                                deckid = 4
                                match(deckid)
                            if deckcode == "5663194":
                                print ("deck suggestion found")
                                deckid = 7
                                match(deckid)
                            if deckcode == "5663491":
                                print ("deck suggestion found")
                                deckid = 7
                                match(deckid)
                            if deckcode == "1621201417":
                                print ("deck suggestion found")
                                deckid = 4
                                match(deckid)
                            if deckcode == "3840344339":
                                print ("no deck suggestion found yet")
                                deckid = 8
                                match(deckid)
                            if deckcode == "565052545146":
                                print ("deck suggestion found yet")
                                deckid = 8
                                match(deckid)
                            if deckcode == "5650525459":
                                print ("deck suggestion found yet")
                                deckid = 8
                                match(deckid)
                            if deckcode == "565054514652":
                                print ("deck suggestion found yet")
                                deckid = 8
                                match(deckid) 
                            if deckcode == "5650525946":
                                print ("no deck suggestion found yet")
                                deckid = 8
                                match(deckid)
                            if deckcode == "5650595246":
                                print ("deck suggestion found yet")
                                deckid = 8
                                match(deckid)
                            if deckcode == "5650575246":
                                print ("deck suggestion found yet")
                                deckid = 8
                                match(deckid)
                            if deckcode == "565052474651":
                                print ("deck suggestion found yet")
                                deckid = 8
                                match(deckid)
                            if deckcode == "565052465451":
                                print ("deck suggestion found yet")
                                deckid = 8
                                match(deckid)
                            #else:
                            #    match(1)
                            print ("____________________________________")
                            break
#match()
#run()

#    acc = Account(user)
#    account_history = list(acc.get_account_history(-1, 5))
#    for transaction in account_history:
#        print (transaction)

if __name__ == '__main__':
    while True:
        try:
            run()
            time.sleep(120)

        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows args to be printed directly,
                                 # but may be overridden in exception subclasse$
            print ("Fehler")



