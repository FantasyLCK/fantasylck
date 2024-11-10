from abc import ABC, abstractmethod
from fractions import Fraction
import random
from typing import Final

from data import UserData, PlayerData

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
    TOP_POINTS: Final[int] = 15
    JGL_POINTS: Final[int] = 25
    MID_POINTS: Final[int] = 25
    ADC_POINTS: Final[int] = 20
    SUP_POINTS: Final[int] = 15

    def __init__(self, user1, user2):
        super().__init__(user1, user2)

    def __value_for_game(self, player: PlayerData) -> int:
        return max(0, player.value + random.randint(-player.trait_weight, player.trait_weight))

    def __determine_points(self, total_points: int, player1: PlayerData, player2: PlayerData):
        p1_value = self.__value_for_game(player1)
        p2_value = self.__value_for_game(player2)
        self._append_player_values(p1_value, p2_value)
        p1_points = Fraction(p1_value, p1_value + p2_value) * total_points
        p2_points = Fraction(p2_value, p1_value + p2_value) * total_points
        return p1_points, p2_points

    def determine_winner(self) -> Fraction:
        top1_points, top2_points = self.__determine_points(PointComparisonLogic.TOP_POINTS, self._user1.top, self._user2.top)
        jgl1_points, jgl2_points = self.__determine_points(PointComparisonLogic.JGL_POINTS, self._user1.jgl, self._user2.jgl)
        mid1_points, mid2_points = self.__determine_points(PointComparisonLogic.MID_POINTS, self._user1.mid, self._user2.mid)
        adc1_points, adc2_points = self.__determine_points(PointComparisonLogic.ADC_POINTS, self._user1.adc, self._user2.adc)
        sup1_points, sup2_points = self.__determine_points(PointComparisonLogic.SUP_POINTS, self._user1.sup, self._user2.sup)
        points1 = top1_points + jgl1_points + mid1_points + adc1_points + sup1_points
        points2 = top2_points + jgl2_points + mid2_points + adc2_points + sup2_points
        return points1 - points2
