from abc import ABC, abstractmethod
from fractions import Fraction
import random
from typing import Final

from data import UserData, PlayerData
from sharing_codes import config

class RosterComparisonLogic(ABC):

    _user1: UserData
    _user2: UserData

    __values: list[tuple[int, int]]

    def __init__(self, user1: UserData, user2: UserData):
        self._user1 = user1
        self._user2 = user2
        self.__values = list()

    @abstractmethod
    def determine_winner(self) -> int:
        ...

    def get_team1_values(self):
        return [self.__values[i][0] for i in range(len(self.__values))]

    def get_team2_values(self):
        return [self.__values[i][1] for i in range(len(self.__values))]

    def _append_player_values(self, value1: int, value2: int):
        self.__values.append((value1, value2))

class PointComparisonLogic(RosterComparisonLogic):
    TOP_POINTS: Final[int] = 17
    JGL_POINTS: Final[int] = 20
    MID_POINTS: Final[int] = 22
    ADC_POINTS: Final[int] = 22
    SUP_POINTS: Final[int] = 19

    __offset: list[tuple[int, int]]

    def __init__(self, user1, user2):
        super().__init__(user1, user2)
        self.__offset = list()

    def __value_for_game(self, player: PlayerData, single: bool) -> tuple[int, int]:
        bonus = config().single_team_bonus if single else 0
        offset = random.randint(-player.trait_weight, player.trait_weight)
        return max(0, player.value + bonus + offset), offset

    def __determine_points(self, total_points: int, player1: PlayerData, player2: PlayerData, single1: bool, single2: bool):
        p1_value, p1_offset = self.__value_for_game(player1, single1)
        p2_value, p2_offset = self.__value_for_game(player2, single2)
        self._append_player_values(p1_value, p2_value)
        self.__offset.append((p1_offset, p2_offset))
        p1_points = Fraction(p1_value, p1_value + p2_value) * total_points
        p2_points = Fraction(p2_value, p1_value + p2_value) * total_points
        return p1_points, p2_points

    def get_team1_offset(self):
        return [self.__offset[i][0] for i in range(len(self.__offset))]

    def get_team2_offset(self):
        return [self.__offset[i][1] for i in range(len(self.__offset))]

    def determine_winner(self) -> Fraction:
        p1_single_team = self._user1.single_team_roster
        p2_single_team = self._user2.single_team_roster
        top1_points, top2_points = self.__determine_points(PointComparisonLogic.TOP_POINTS, self._user1.top, self._user2.top, p1_single_team, p2_single_team)
        jgl1_points, jgl2_points = self.__determine_points(PointComparisonLogic.JGL_POINTS, self._user1.jgl, self._user2.jgl, p1_single_team, p2_single_team)
        mid1_points, mid2_points = self.__determine_points(PointComparisonLogic.MID_POINTS, self._user1.mid, self._user2.mid, p1_single_team, p2_single_team)
        adc1_points, adc2_points = self.__determine_points(PointComparisonLogic.ADC_POINTS, self._user1.adc, self._user2.adc, p1_single_team, p2_single_team)
        sup1_points, sup2_points = self.__determine_points(PointComparisonLogic.SUP_POINTS, self._user1.sup, self._user2.sup, p1_single_team, p2_single_team)
        points1 = top1_points + jgl1_points + mid1_points + adc1_points + sup1_points
        points2 = top2_points + jgl2_points + mid2_points + adc2_points + sup2_points
        return points1 - points2
