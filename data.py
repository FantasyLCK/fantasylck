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
    def create_new_entry(player_id, name, position, team, tier, trait_weight) -> tuple['PlayerData', bool]:
        entry = players_collection.find_one({'player_id': player_id})
        logger.debug(f"entry = {entry}")
        if entry is not None:
            return PlayerData(entry['player_id']), False

        players_collection.update_one(
            {'player_id': player_id},
            {'$set': {
                'name': name,
                'position': position,
                'team': team,
                'tier': tier,
                'trait_weight': trait_weight
            }},
            upsert=True
        )
        return PlayerData(player_id), True

class UserData:
    def __init__(self, user_id, discord_id, player_list, balance=150, login_record=None):
        self.user_id = user_id
        self.discord_id = discord_id
        self.player_list = player_list or []
        self.balance = balance
        self.login_record = login_record or []

    @staticmethod
    def load_from_db(user_id):
        data = users_collection.find_one({'user_id': user_id})
        if data:
            return UserData(data['user_id'],
                              data['discord_id'],
                              data['player_list'],
                              data['balance'],
                              data['login_record'])
        else:
            print("User not found in database.")
            return None

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

    def update_balance(self, amount):
        self.balance += amount
        self.save_to_db()

    def add_login_record(self, record_time=None):
        if not record_time:
            record_time = datetime.now()
        self.login_record.append(record_time)
        self.save_to_db()

    @staticmethod
    def delete_from_db(name):
        users_collection.delete_one({'name': name})


    @staticmethod
    def get_team_value(self):
        total_value = 0
        for player in self.player_list:
            if player:
                total_value += player.value
        return total_value

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
                player_id=player_info['player_id'],
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
                player_id=player_info['player_id'],
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

    # If users_data is a list (not dictionary), handle the case
    if isinstance(users_data, list):
        for user_info in users_data:
            user = UserData(
                user_id=user_info['user_id'],
                discord_id=user_info['discord_id'],
                player_list=user_info['player_list'],
                balance=user_info['balance'],
                login_record=user_info['login_record']
            )
            user.save_to_db()  # Save user data to MongoDB
            print(f"User {user_info['discord_id']} saved to the database.")
    elif isinstance(users_data, dict):
        for user_id, user_info in users_data.items():
            user = UserData(
                user_id=user_info['user_id'],
                discord_id=user_info['discord_id'],
                player_list=user_info['player_list'],
                balance=user_info['balance'],
                login_record=user_info['login_record']
            )
            user.save_to_db()  # Save user data to MongoDB
            print(f"User {user_info['discord_id']} saved to the database.")
    else:
        print("Users data is neither a list nor a dictionary, skipping database update.")
