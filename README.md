Basically, there are three files at the moment. All three are written in Python 3.6

tradingbotbuyer.py
This program will consistently scan the market for new cards. Whenever a new card comes to the market, it identifies the card and checks what limit the user has set for the card. If the price of the card is below the set limit, it will buy the card. To make sure that no cards are paid multiple times, each transaction is saved in a mongo db.

The bot takes care of limits for different rarities but also allows to set limits for individual cards. The limits can either be set directly in the code or by querying the blockchain. This requires to save the settings in a specific format into the blockchain by making a transaction to a specified reference account.

Additionally, it differentiates between gold foil and normal cards and for the normal cards also picks up if a card is leveled. As of now the bot does not differentiate between Alpha and Beta cards.

Finally, there is also a feature to set a max holding limit for each card. This means that if you set 300 as a limit, the bot will stop buying a specific card if the limit is exceeded.

Lastly, there is also the option to shut down the bot via a certain command written into the blockchain.

tradingbotseller.py
This bot will put your cards on the market. Again, you can set limits for different cards or rarities and you can also set a limit for the maximum number of cards for each card you want to put on the market at a time.

The bot will again and again go through your cards and check every card if the price o the market is still consistent with your limits. If it is not, it will cancel your sale and create a new sell order.

Another feature is the "underbidding" function. This will set the price just below the current lowest sales price - but at least at your set limit.

A big weakness of this part of the bot is the fact that I have not yet implement beta cards, but this should be relative easy to do.

fightbot.py
The fightbot is a basic fightbot that will battle automatically. It is not very smart and will not get you up high in the rankings. But it helps to explain how the fighting algorithm works and might be used as a basis for future work.

