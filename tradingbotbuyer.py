from steem import Steem
from steem.blockchain import Blockchain
from steem.account import Account
from steem.post import Post
import json
import time
import datetime
import requests
import pymongo

parameteraccount = "golddragon"
user = "STEEMUSERNAME"
steem = Steem(nodes=["https://api.steemit.com"],
          keys=["PRICATEACTIVEKEY"])

latest = 0
account = Account(parameteraccount)
botactive = True


def get_parameters():
    #this function is used to get the different trading parameters from the blockchain
    account_history = list(account.get_account_history(-1, 10000, filter_by=["transfer"]))
    for transaction in account_history:
        memo = transaction["memo"]
        #print (memo)
        fromaccount = transaction["from"]
        if memo.startswith('smtb') and fromaccount == user:
            code, parameters = transaction["memo"].split("@")
            #print (parameters)
            return (parameters)


# Lege die Parameter für die Datenbank fest
mongo_collection = pymongo.MongoClient()["steem_monsters_db"]["transactions"]

# Lege die Parameter fest, wo ich die Raritydaten bekomme
url = 'https://steemmonsters.com/cards/get_details'
r = requests.get(url)
monsters = r.json()


# Lege Schwellenwerte für die einzelnen Rarities und Monster fest, unter denen der Bot kauft
normal_hurdles = {1:0.01,2:0.15,3:0.35,4:6.5}
gold_hurdles = {1:2.2,2:6.5,3:20,4:150}
gold_hurdles_special = {5:9,16:9,27:9,38:9,49:9,23:3.5,35:3.5,26:3.5,56:200,57:200,58:200,59:250}
normal_hurdles_special = {5:0.2,16:0.2,27:0.2,38:0.2,49:0.2,23:0.09,35:0.09,26:0.09,56:9,57:9,58:9,59:9}
#Lege den maximalen Bestand pro Karte fest
card_limit_normal = {1:500,2:200,3:100,4:10}
card_limit_gold = {1:10,2:10,3:100,4:100}

#definiere die XP pro Level nach Rarity
xp_per_level = {1:2,2:10,3:25,4:100}

def check_if_old(memotext):
    # Checks vs a database if a transaction has been used already
    check = True
    db = mongo_collection.find().sort('timestamp',-1).limit(50)
    #print (db)
    for data in db:
        memo = data["memo"]
        if memo == memotext:
            check = False
            return (check)
    return (check)

def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def getmonsterdetails(id,attribute):
    for monster in monsters:
        if monster['id'] == int(id):
            return (monster[attribute])

def autobuyer():
    # Holt sich die aktuellen Limits
    try:
        parameters = get_parameters()
        data = json.loads(parameters)
        normal_hurdles = data["buy_normal_hurdles"]
        normal_hurdles_special = data["buy_normal_hurdles_special"]
        gold_hurdles = data["buy_gold_hurdles"]
        gold_hurdles_special = data["buy_gold_hurdles_special"]
        card_limit_normal = data["card_limit_normal"]
        card_limit_gold  = data["card_limit_gold"]
    except:
        print("Fehler beim Laden der Kauflimite")

    # get the latest SBD feed from steemmonsters account
    sbdusd = getsbdprice()

    #r = requests.get('https://api.coinmarketcap.com/v1/ticker/steem/')
    #for coin in r.json():
    #    steemusd = float(coin["price_usd"])
    #r = requests.get('https://api.coinmarketcap.com/v1/ticker/steem-dollars/')
    #for coin in r.json():
    #    sbdusd = float(coin["price_usd"])

    # Hole alle Verkäufe aus der Steem Monsters API

    # Ermittele  den letzten Block aus der Blockchain
    lastblock = steem.head_block_number
    print (lastblock)
    print ("Letzter Block in der Blockchain:" +str(lastblock))
    startblock = lastblock -20

    #lade die API
    r = requests.get('https://steemmonsters.com/transactions/history?from_block=' +str(startblock))
    data = r.json()
    for transaction in data:
        if transaction['type'] == 'sm_sell_cards':
            raw_transactiondata = transaction['data']
            transactiondata = json.loads(raw_transactiondata)[0]
            seller = str(transaction['player'])
            trx = str(transaction['id'])
            price = float(transactiondata['price'])
            cardid = transactiondata['cards'][0]
            print ("=====================================")
            print (seller)
            print (price)
            print (cardid)
            print (trx)

            # Ermittele die Rarity der Karte und ob es Gold Foil ist
            (monsterid,rarity,gold,name,xp,buy_price,player) = get_card_details(cardid)

            #Ermittele unseren Bestand
            stock = get_card_stock(cardid)
            text = ("Cardid: " + cardid + ", Rarity: " +  str(rarity) + ", Price: " + str(price) + " Seller: " +str(seller) + ".")
            print (text)

            # Prüfe of der  Preis unter dem entsprechenden Schwellenwert  liegt
            try:
                if gold == True:
                    try:
                        hurdle = float(gold_hurdles_special[str(monsterid)])
                    except:
                        hurdle = float(gold_hurdles[str(rarity)])
                    print ("Hürde:" +str(hurdle))
                    # wenn der Preis unter der Hurdle Rate liegt und unter dem Bestandlimit:
                    if (price <= hurdle) and (stock <= float(card_limit_gold[str(rarity)])) and (seller != user):
                        go = True
                        print ("Billige Karte gefunden")
                        memotext = "sm_market_purchase:" + trx + "-0"
                        SBD = round((price) /float(sbdusd),3)
                        go = check_if_old(memotext)
                        if go == True:
                            print ("Überweisung wird initialisiert")
                            try:
                                SBD = SBD
                                steem.transfer('steemmonsters', amount=SBD, asset="SBD", memo=memotext, account=user)
                                print ("Überweisung beendet")
                                ts = datetime.datetime.now().timestamp()
                                dbinput = {"memo": memotext, "timestamp":ts}
                                mongo_collection.insert_one(dbinput).inserted_id
                                #tim.sleep(45)
                            except Exception as inst:
                                print(type(inst))    # the exception instance
                                print(inst.args)     # arguments stored in .args
                                print(inst)          # __str__ allows args to be printed directly,
                                                     # but may be overridden in exception subclasse$
                                print ("Überweisungsfehler")

                else:
                    if float(xp) > 0:
                        cardnumber = ((xp / 10) / float(xp_per_level[rarity])) + 1
                        print ("Anzahl der kombinierten Karten : " +str(cardnumber))
                    else:
                        cardnumber = 1
                    try:
                        hurdle = normal_hurdles_special[str(monsterid)] * float(cardnumber)
                    except:
                        hurdle = float(normal_hurdles[str(rarity)]) * float(cardnumber)
                    print ("Hürde:" +str(hurdle))

                    # wenn der Preis unter der Hurdle Rate liegt und unter dem Bestandslimit:
                    if (price <= hurdle) and (stock <= float(card_limit_normal[str(rarity)])) and (seller != user):
                        go = True
                        print ("Billige Karte gefunden")
                        memotext = "sm_market_purchase:" + trx + "-0"
                        SBD = round((price) /float(sbdusd),3)
                        #Check ob schon einmal überwiesen wurde
                        go = check_if_old(memotext)
                        if go == True:
                            print ("Überweisung wird initialisiert")
                            try:
                                SBD = SBD
                                print (SBD)
                                print (memotext)
                                print (seller)
                                steem.transfer('steemmonsters', amount=SBD, asset="SBD", memo=memotext, account=user)
                                print ("Überweisung beendet")
                                ts = datetime.datetime.now().timestamp()
                                dbinput = {"memo": memotext, "timestamp":ts}
                                mongo_collection.insert_one(dbinput).inserted_id
                                #time.sleep(45)

                            except Exception as inst:
                                print(type(inst))    # the exception instance
                                print(inst.args)     # arguments stored in .args
                                print(inst)          # __str__ allows args to be printed directly,
                                                         # but may be overridden in exception subclasse$
                                print ("Überweisungsfehler")
            except Exception as inst:
                print(type(inst))    # the exception instance
                print(inst.args)     # arguments stored in .args
                print(inst)          # __str__ allows args to be printed directly,
                                     # but may be overridden in exception subclasse$
                print ("Fehler")
                continue

def get_card_details(card_id):
    # get the carddetails from steemmonsters.com
    r = requests.get("https://steemmonsters.com/cards/find?ids=" + card_id)
    data = r.json()
    player = data[0]["player"]
    monsterid = data[0]["card_detail_id"]
    xp = data[0]["xp"]
    buy_price = data[0]["buy_price"]
    market_id = data[0]["market_id"]
    gold = data[0]["gold"]
    details = data[0]["details"]
    type = details["type"]
    name = details["name"]
    rarity = details["rarity"]
    #print (monsterid)
    #print (name)
    #print (rarity)
    #print ("-------")

    return(monsterid,rarity,gold,name,xp,buy_price,player)


def get_card_stock(card_id):
    stock = 0
    (monsterid,rarity,gold,name,xp,buy_price,player) = get_card_details(card_id)

    # get all cards in stock
    r = requests.get('https://steemmonsters.com/cards/collection/' +str(user))
    data = r.json()
    for card in data["cards"]:
        monsterid == card["card_detail_id"]
        xp = card["xp"]
        buy_price = card["buy_price"]
        market_id = card["market_id"]
        if monsterid == card["card_detail_id"] and gold == card["gold"]:
            stock = stock +1

    print ("Current stock: " + str(stock))
    return(stock)

def getsbdprice():
    #get the last transactions of steemmonsters from the blockchain
    acc = Account('steemmonsters')
    account_history = acc.get_account_history(-1, 1000, filter_by=["custom_json"])
    for custom_json in account_history:
        try:
            data = custom_json["json"]
            parsed_json = json.loads(data)
            code = custom_json["id"]
            if code == "sm_price_feed":
                sbd = parsed_json["sbd"]
                return(sbd)
        except:
            print ("Error getting the SBD price")

if __name__ == '__main__':
    while True:
        try:
            parameters = get_parameters()
            data = json.loads(parameters)
            botactive = data["botactive"]
            sell_normal_hurdles = data["sell_normal_hurdles"]
            if botactive == True:
                autobuyer()
            else:
                print ("Bot is currently deactivated")

        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows args to be printed directly,
                                     # but may be overridden in exception subclasse$
            print ("Fehler")
            continue

