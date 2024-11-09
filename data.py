import json
import logging
from typing import Self

from pymongo import MongoClient
from datetime import datetime

logger = logging.getLogger('data')

client = MongoClient("mongodb://localhost:27017/")
db = client["FantasyLCK"]
players_collection = db["players"]
users_collection = db["users"]

class PlayerData:

    __player_id: int

    def __init__(self, player_id: int):
        self.__player_id = player_id

    def __save_to_db(self):
        players_collection.update_one(
            {'player_id': self.player_id},
            {'$set': {
                'name': self.name,
                'position': self.position,
                'team': self.team,
                'tier': self.tier,
                'trait_weight': self.trait_weight
            }},
            upsert=True
        )

    @staticmethod
    def load_from_db(player_id: int = -1, player_name: str = None):
        if player_id is not None:
            data = players_collection.find_one({'player_id': player_id})
        elif player_name is not None:
            data = players_collection.find_one({'name': player_name})
        else:
            raise ValueError
        if data is not None:
            return PlayerData(data['player_id'])
        else:
            raise ValueError("Player not found in database.")

    def __retrieve_db(self):
        return players_collection.find_one({'player_id': self.__player_id})

    @property
    def name(self) -> str:
        return self.__retrieve_db()['name']

    @property
    def position(self) -> str:
        return self.__retrieve_db()['position']

    @property
    def team(self) -> str:
        return self.__retrieve_db()['team']

    @property
    def tier(self) -> str:
        return self.__retrieve_db()['tier']

    @property
    def trait_weight(self):
        return self.__retrieve_db()['trait_weight']

    def delete(self):
        players_collection.delete_one({'player_id': self.__player_id})

    @staticmethod
    def delete_from_db(name):
        players_collection.delete_one({'name': name})

    @staticmethod
    def create_new_entry(id, name, position, team, tier, trait_weight) -> tuple['PlayerData', bool]:
        entry = PlayerData.load_from_db(player_id=id)
        logger.debug(f"entry = {entry}")
        if entry is not None:
            return entry, False

        players_collection.update_one(
            {'player_id': id},
            {'$set': {
                'name': name,
                'position': position,
                'team': team,
                'tier': tier,
                'trait_weight': trait_weight
            }},
            upsert=True
        )
        return PlayerData(id), True

class UserData:

    __discord_id: int

    def __init__(self, discord_id):
        self.__discord_id = discord_id

    def __retrieve_db(self):
        return users_collection.find_one({'discord_id': self.__discord_id})

    @staticmethod
    def load_from_db(discord_id):
        data = users_collection.find_one({'discord_id': discord_id})
        if data:
            return UserData(data['discord_id'])
        else:
            print("User not found in database.")
            return None

    @property
    def balance(self) -> int:
        return self.__retrieve_db()['balance']

    @property
    def top(self) -> PlayerData:
        id = self.__retrieve_db()['top']
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def jgl(self) -> PlayerData:
        id = self.__retrieve_db()['jgl']
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def mid(self) -> PlayerData:
        id = self.__retrieve_db()['mid']
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def adc(self) -> PlayerData:
        id = self.__retrieve_db()['adc']
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def sup(self) -> PlayerData:
        id = self.__retrieve_db()['sup']
        if id < 0:
            return None
        return PlayerData(id)

    def save_to_db(self):
        users_collection.update_one(
            {'user_id': self.user_id},
            {'$set': {
                'discord_id': self.discord_id,
                'player_list': self.player_list,
                'balance': self.balance,
                'login_record': self.login_record,
            }},
            upsert=True
        )

    def update_balance(self, amount: int):
        if (amount < 0) and self.balance < abs(amount):
            raise ValueError
        users_collection.update_one(
            {'discord_id': self.__discord_id},
            {'$set': {
                'balance': self.balance + amount
            }},
            upsert=True
        )

    def add_login_record(self, record_time=None):
        if not record_time:
            record_time = datetime.now()
        self.login_record.append(record_time)
        self.save_to_db()

    @staticmethod
    def delete_from_db(name):
        users_collection.delete_one({'name': name})


    @property
    def team_value(self) -> int:
        total_value = 0
        for player in [self.top, self.jgl, self.mid, self.adc, self.sup]:
            if player is not None:
                total_value += player.value
        return total_value

    @staticmethod
    def create_new_entry(id, top, jgl, mid, adc, sup, balance, login_record) -> tuple['UserData', bool]:
        entry = UserData.load_from_db(discord_id=id)
        logger.debug(f"entry = {entry}")
        if entry is not None:
            return entry, False

        users_collection.update_one(
            {'discord_id': id},
            {'$set': {
                'top': top,
                'jgl': jgl,
                'mid': mid,
                'adc': adc,
                'sup': sup,
                'balance': balance,
                'login_record': login_record
            }},
            upsert=True
        )
        return PlayerData(id), True

# Function to load data from JSON files and save to MongoDB
def load_and_save_data():
    # Load players data from players.json
    try:
        with open('players.json', 'r', encoding='utf-8') as f:
            players_data = json.load(f)
            print("Type of players_data:", type(players_data))  # Debug: type of the loaded data
            print("Loaded players data:", players_data)  # Debug print to inspect the structure
    except Exception as e:
        print(f"Error loading players data: {e}")
        return

    # If players_data is a list (not dictionary), handle the case
    if isinstance(players_data, list):
        for player_info in players_data:
            player, result = PlayerData.create_new_entry(
                id=player_info['player_id'],
                name=player_info['name'],
                position=player_info['position'],
                team=player_info['team'],
                tier=player_info['tier'],
                trait_weight=player_info['trait_weight']
            )
            if result:
                logger.info(f"Player {player_info['name']} saved to the database.")
            else:
                logger.info(f"Player {player_info['name']} already exists in the database.")
    elif isinstance(players_data, dict):
        for player_id, player_info in players_data.items():
            player, result = PlayerData.create_new_entry(
                id=player_info['player_id'],
                name=player_info['name'],
                position=player_info['position'],
                team=player_info['team'],
                tier=player_info['tier'],
                trait_weight=player_info['trait_weight']
            )
            if result:
                logger.info(f"Player {player_info['name']} saved to the database.")
            else:
                logger.info(f"Player {player_info['name']} already exists in the database.")
    else:
        print("Players data is neither a list nor a dictionary, skipping database update.")

    # Load users data from users.json
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            print("Type of users_data:", type(users_data))  # Debug: type of the loaded data
            print("Loaded users data:", users_data)  # Debug print to inspect the structure
    except Exception as e:
        print(f"Error loading users data: {e}")
        return

    for user_info in users_data:
        user, result = UserData.create_new_entry(
            id = user_info['discord_id'],
            top = user_info['discord_id'],
            jgl = user_info['jgl'],
            mid = user_info['mid'],
            adc = user_info['adc'],
            sup = user_info['sup'],
            balance = user_info['balance'],
            login_record = user_info['login_record']
        )
        if result:
            logger.info(f"User {user_info['discord_id']} saved to the database.")
        else:
            logger.info(f"User {user_info['discord_id']} already exists in the database.")
