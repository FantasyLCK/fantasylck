import json
import logging
from typing import Self

from datetime import datetime

from db_connection import db
from sharing_codes import config

logger = logging.getLogger('data')

def players_collection():
    return db["players"]

def users_collection():
    return db["users"]

# 선수의 티어에 따라 비용을 계산하는 함수
def get_player_cost(tier: str) -> int:
    tier_costs = config().tier_values
    return tier_costs.get(tier, 0)

class PlayerData:

    __player_id: int

    def __init__(self, player_id: int):
        self.__player_id = player_id

    def __save_to_db(self):
        players_collection().update_one(
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
        if player_id >= 0:
            data = players_collection().find_one({'player_id': player_id})
        elif player_name is not None:
            data = players_collection().find_one({'name': player_name})
        else:
            raise ValueError
        if data is not None:
            return PlayerData(data['player_id'])
        else:
            raise ValueError("Player not found in database.")

    def __retrieve_db(self):
        return players_collection().find_one({'player_id': self.__player_id})

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

    @property
    def id(self):
        return self.__player_id
    
    @property
    def value(self):
        return get_player_cost(self.tier)

    def delete(self):
        players_collection().delete_one({'player_id': self.__player_id})

    @staticmethod
    def delete_from_db(name):
        players_collection().delete_one({'name': name})

    @staticmethod
    def create_new_entry(id, name, position, team, tier, trait_weight) -> tuple['PlayerData', bool]:
        try:
            return PlayerData.load_from_db(player_id=id), False
        except ValueError:
            players_collection().update_one(
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
        return users_collection().find_one({'discord_id': self.__discord_id})

    @staticmethod
    def load_from_db(discord_id) -> 'UserData':
        data = users_collection().find_one({'discord_id': discord_id})
        if data:
            return UserData(data['discord_id'])
        else:
            raise ValueError("User not found in database.")

    @property
    def balance(self) -> int:
        return self.__retrieve_db()['balance']

    @property
    def top(self) -> PlayerData:
        id = self.top_id
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def top_id(self) -> PlayerData:
        return self.__retrieve_db()['top']
    
    @top_id.setter
    def top_id(self, id: int):
        if (self.top_id >= 0 and id >= 0):
            raise AttributeError
        users_collection().update_one(
            {'discord_id': self.__discord_id},
            {'$set': {
                'top': id
            }},
            upsert=True
        )

    @property
    def jgl(self) -> PlayerData:
        id = self.jgl_id
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def jgl_id(self) -> PlayerData:
        return self.__retrieve_db()['jgl']
    
    @jgl_id.setter
    def jgl_id(self, id: int):
        if (self.jgl_id >= 0 and id >= 0):
            raise AttributeError
        users_collection().update_one(
            {'discord_id': self.__discord_id},
            {'$set': {
                'jgl': id
            }},
            upsert=True
        )

    @property
    def mid(self) -> PlayerData:
        id = self.mid_id
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def mid_id(self) -> PlayerData:
        return self.__retrieve_db()['mid']
    
    @mid_id.setter
    def mid_id(self, id: int):
        if (self.mid_id >= 0 and id >= 0):
            raise AttributeError
        users_collection().update_one(
            {'discord_id': self.__discord_id},
            {'$set': {
                'mid': id
            }},
            upsert=True
        )

    @property
    def adc(self) -> PlayerData:
        id = self.adc_id
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def adc_id(self) -> PlayerData:
        return self.__retrieve_db()['adc']
    
    @adc_id.setter
    def adc_id(self, id: int):
        if (self.adc_id >= 0 and id >= 0):
            raise AttributeError
        users_collection().update_one(
            {'discord_id': self.__discord_id},
            {'$set': {
                'adc': id
            }},
            upsert=True
        )

    @property
    def sup(self) -> PlayerData:
        id = self.sup_id
        if id < 0:
            return None
        return PlayerData(id)

    @property
    def sup_id(self) -> PlayerData:
        return self.__retrieve_db()['sup']
    
    @sup_id.setter
    def sup_id(self, id: int):
        if (self.sup_id >= 0 and id >= 0):
            raise AttributeError
        users_collection().update_one(
            {'discord_id': self.__discord_id},
            {'$set': {
                'sup': id
            }},
            upsert=True
        )

    def update_balance(self, amount: int):
        if (amount < 0) and self.balance < abs(amount):
            raise ValueError
        users_collection().update_one(
            {'discord_id': self.__discord_id},
            {'$set': {
                'balance': self.balance + amount
            }},
            upsert=True
        )

    @property
    def login_record(self):
        return self.__retrieve_db()['login_record']

    @login_record.setter
    def update_login_record(self, record_time):
        users_collection().update_one(
            {'discord_id': self.__discord_id},
            {'$set': {
                'record_time': record_time
            }},
            upsert=True
        )

    @staticmethod
    def delete_from_db(name):
        users_collection().delete_one({'name': name})


    @property
    def team_value(self) -> int:
        total_value = 0
        for player in [self.top, self.jgl, self.mid, self.adc, self.sup]:
            if player is not None:
                total_value += player.value
        return total_value

    @staticmethod
    def create_new_entry(id: int, top: int = -1, jgl: int = -1, mid: int = -1, adc: int = -1, sup: int = -1, balance: int = 0, login_record: int = 0) -> tuple['UserData', bool]:
        try:
            return UserData.load_from_db(discord_id=id), False
        except ValueError:
            users_collection().update_one(
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
