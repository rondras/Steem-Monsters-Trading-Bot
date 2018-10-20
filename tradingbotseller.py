from steem.transactionbuilder import TransactionBuilder
from steembase import operations
from steem import Steem
from steem.blockchain import Blockchain
from steem.account import Account
from steem.post import Post
import json
import datetime
import requests

parameteraccount = "golddragon"
user = "STEEMUSERNAME"

acc = Account(parameteraccount)
s = Steem(nodes=["https://steemd.privex.io"],
          keys=["PRIVATEPOSTINGKEY"])

#lege fest ob unterbieten angeschaltet ist
underbidding = False

# Lege die Parameter fest, wo ich die Raritydaten bekomme
url = 'https://steemmonsters.com/cards/get_details'
r = requests.get(url)
monsters = r.json()


def get_parameters():
    #this function is used to get the different trading parameters from the blockchain
    account_history = list(acc.get_account_history(-1, 10000, filter_by=["transfer"]))
    for transaction in account_history:
        memo = transaction["memo"]
        #print (memo)
        fromaccount = transaction["from"]
        if memo.startswith('smtb') and fromaccount == user:
            code, parameters = transaction["memo"].split("@")
            #print (parameters)
            return (parameters)

#Lege das Bestandslimit fest
orderlimit = {"1":10,"2":10,"3":10,"4":10}

def getlowestprice(monstercode):
    # get all offers from steemmonsters.com
    r = requests.get('https://steemmonsters.com/market/for_sale')
    data = r.json()    
    lowestprice_normal = 1000000
    lowestprice_gold = 1000000
    for card in data:
        seller = card['seller']
        gold  = card['gold']
        card_detail_id = card['card_detail_id']
        buy_price = card["buy_price"]
        if (int(card_detail_id) == int(monstercode)) and (gold == True) and (seller != user):
            if float(buy_price) < float(lowestprice_gold):
                lowestprice_gold = buy_price
        if (int(card_detail_id) == int(monstercode)) and (gold == False) and (seller!= user):
            if float(buy_price) < float(lowestprice_normal):
                lowestprice_normal = buy_price
    return (lowestprice_gold, lowestprice_normal)

def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def getmonsterdetails(id,attribute):
    for monster in monsters:
        if monster['id'] == int(id):
            return (monster[attribute])

def sell(cardid,price):
    json = [{"cards":[cardid],"currency":"USD","price":str(price),"fee_pct":500}]
    print (json)
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_sell_cards",
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

def cancelorder(cardid):
    # ermittele die market_id
    r = requests.get('https://steemmonsters.com/market/for_sale')
    data = r.json()
    for card in data:
        uid = card['uid']
        market_id = card['market_id']
        if cardid == uid:
            trxid = market_id
    #baue die Transaktion auf
    json = {"trx_id":trxid}
    print (json)
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_cancel_sell",
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

def getprice(monsterid):
    # Holt sich die aktuellen Kauflimite
    try:
        parameters = get_parameters()
        data = json.loads(parameters)
        normal_hurdles = data["sell_normal_hurdles"]
        normal_hurdles_special = data["sell_normal_hurdles_special"]
        gold_hurdles = data["sell_gold_hurdles"]
        gold_hurdles_special = data["sell_gold_hurdles_special"]

    except:
        print("Fehler beim Laden der Kauflimite - nimm Standardwerte")
        normal_hurdles = {1:0.06,2:0.22,3:0.59,4:9.9}
        gold_hurdles = {1:3.49,2:12.9,3:44,4:390}
        gold_hurdles_special = {5:19.9,16:19.9,27:19.9,38:19.9,49:19.9,23:150,35:100,26:100,56:2000,57:490,58:490,59:490}
        normal_hurdles_special = {5:0.33,16:0.33,27:0.33,38:0.33,49:0.33,23:1,26:1,35:1,56:12.90,57:11.90,58:11.90,59:11.90}

    # get the carddetails from steemmonsters.com
    r = requests.get('https://steemmonsters.com/cards/collection/' +str(user))
    data = r.json()

    #finde den richtigen Verkaufspreis
    rarity = getmonsterdetails(monsterid,"rarity")
        #ermittele unseren Minimumpreis
    try:
        minpricegold = float(gold_hurdles_special[str(monsterid)])
    except:
        minpricegold = float(gold_hurdles[str(rarity)])
    try:
        minpricenormal = float(normal_hurdles_special[str(monsterid)])
    except:
        minpricenormal = float(normal_hurdles[str(rarity)])

    #ermittele den niedrigsten Marktpreis
    (lowestprice_gold, lowestprice_normal) = getlowestprice(monsterid)

    # setze den Preis aus den beiden Werten zusammen
    if (float (minpricegold)+0.01) < float(lowestprice_gold) and (underbidding == True):
       goldprice = float(lowestprice_gold) - 0.01
    else:
       goldprice = float(minpricegold)

    # dann für normal
    if (float (minpricenormal)+0.01) < float(lowestprice_normal) and (underbidding == True):
       normalprice = float(lowestprice_normal) - 0.01
    else:
       normalprice = float(minpricenormal)
    return (normalprice,goldprice)

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
        gold = card["gold"]
        if monsterid == card["card_detail_id"] and gold == card["gold"]:
            stock = stock +1

    print ("Current stock: " + str(stock))
    return(stock)

def get_card_market_stock(card_id):
    marketstock = 0
    (monsterid,rarity,gold,name,xp,buy_price,player) = get_card_details(card_id)
    # get all cards in stock
    r = requests.get('https://steemmonsters.com/cards/collection/' +str(user))
    data = r.json()
    for card in data["cards"]:
        monster_id = str(card["card_detail_id"])
        card_gold = card["gold"]
        xp = card["xp"]
        buy_price = card["buy_price"] 
        market_id = card["market_id"]
        if buy_price is None:
            onmarket = False
        else:
            onmarket = True
        if (str(monsterid) == str(monster_id)) and (gold == card_gold) and (onmarket == True):
            marketstock = marketstock +1
    print ("Current market stock: " + str(marketstock))
    return (marketstock)

def autoseller():
    # get the carddetails from steemmonsters.com
    r = requests.get('https://steemmonsters.com/cards/collection/' +str(user))
    data = r.json()
    for card in data["cards"]:
        try:
            player = card["player"]
            uid = card["uid"]
            (monsterid,rarity,gold,name,xp,buy_price,player) = get_card_details(uid)
            #monsterid = card["card_detail_id"]
            #xp = card["xp"]
            #buy_price = card["buy_price"]
            market_id = card["market_id"]
            #gold = card["gold"]
            print (uid)
            print ("Aktueller Verkaufspreise: " +str(buy_price))
            # ermittele unseren aktuellen Bestand der Karte
            marketstock = get_card_market_stock(uid)
            # ermittele den aktuell richtigen Preis
            (normalprice,goldprice) = getprice(monsterid)
            print ("Correct new normal price: " +str(normalprice))
            print ("Correct new gold price: " +str(goldprice))
            # ermittele die richtige Order Size - MUSS NOCH NACHGEBSSERT WERDEN
            try:
                parameters = get_parameters()
                data = json.loads(parameters)
                orderlimit = data["orderlimit"]
                targetorder = orderlimit[str(rarity)]  
                print (targetorder)
            except:
                targetorder = orderlimit[str(rarity)]
                print ("Fehler beim Ermitteln der Target order")

            if buy_price is None:
                # check ob maximaler Bestand unterschritte:
                if marketstock < targetorder:
                    #Stelle die Karte zum Verkauf
                    print ("Karte wird zum Verkauf gestellt")
                    #ermittele den richtigen Preis
                    (normalprice,goldprice) = getprice(monsterid)
                    if gold == True:
                        sell(uid,goldprice)

                    else:
                        if int (xp) == 0:
                            sell(uid,normalprice)
                else:
                    print ("Maximalw Verkaufsmenge bereits erreicht")

            else:
                if gold == True:
                    if  float(goldpreis) != float(buy_price):
                        #cancel die bestehende Order
                        print ("Bestehende Order wird gecancelt")
                        cancelorder(uid)
                        marketstock = marketstock - 1
                        print ("Order wurde gecancelt")
                        if marketstock <= targetorder:
                            sell(uid,goldprice)
                            print ("Karte wurde neu zum Verkauf gestellt")
                        else:
                            print ("Orderlimit bereits erreicht")
                    else:
                        print ("Preis ist noch aktuell")
                        if marketstock > targetorder:
                            print ("Zuviele Orders eingestellt. Bestehende Order wird gecancelt")
                            cancelorder(uid)
                else:
                    print ("Karte wurde bereits eingestellt")
                    try:
                        if  float(normalprice) != float(buy_price):
                            #cancel die bestehende Order
                            print ("Bestehende Order wird gecancelt")
                            cancelorder(uid)
                            marketstock = marketstock - 1
                            print ("Order wurde gecancelt")
                            if marketstock <= targetorder and int(xp) == 0:
                                sell(uid,normalprice)
                                print ("Karte wurde neu zum Verkauf gestellt")
                            else:
                                print ("Maximale Verkaufsmenge bereits erreicht")
                        else:
                            print ("Preis ist noch aktuell")
                            if marketstock > targetorder:
                                print ("Zuviele Orders eingestellt. Bestehende Order wird gecancelt")
                                cancelorder(uid)
 
                    except:
                         print ("Fehler bei einer Karte die bereits eingestellt war")
        except:
            print ("Problem mit dieser Karte")

if __name__ == '__main__':
    while True:
        try:
            parameters = get_parameters()
            data = json.loads(parameters)
            botactive = data["botactive"]
            #underbidding = data["underbidding"]
            if botactive == True:
                autoseller()
            else:   
                print ("Bot is currently deactivated")
            #r = requests.get("http://bot.crossbot.de/hurdlesneu.json")
            #data = data = r.json()
            #underbidding = data["underbidding"]
            #print ("Underbidding:")
            #print (underbidding)
            #autoseller()
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows args to be printed directly,
                                 # but may be overridden in exception subclasse$
            print ("Fehler")

