from __future__ import annotations
from dataclasses import dataclass
from random import choice

from text_to_emoji import translate_text
from game_data_manager import DataManager
from game_data_manager import Song

STARTING_LIVES: int = 3
OPTION_COUNT: int = 3
BAR_COUNT: int = 3


@dataclass
class Guess:
    song: Song
    is_correct: bool


@dataclass
class Level:
    options: list[Song]
    correct: Song
    bars: list[str]

    def get_emoji_bars(self) -> list[str]:
        return [translate_text(bar) for bar in self.bars]

    @staticmethod
    def new_level(played_songs: list[Song] | None = None) -> Level:
        if played_songs is None:
            played_songs = []
        options: list[Song] = DataManager.get().get_songs(played_songs=played_songs,
                                                          n=OPTION_COUNT)
        correct: Song = choice(options)
        bars: list[str] = correct.lyrics.get_random_bars(n=BAR_COUNT)
        return Level(options, correct, bars)


class GameState:

    def __init__(self) -> None:
        self.level: Level = Level.new_level()
        self.played_songs: list[Song] = [self.level.correct]
        self.guesses: list[Guess] = []
        self.game_over: bool = False

    def get_lives(self) -> int:
        wrong_guesses: int = len(self.guesses) - self.get_score()
        return STARTING_LIVES - wrong_guesses

    def get_score(self) -> int:
        return len(list(filter(lambda guess: guess.is_correct, self.guesses)))

    def guess(self, option: Song) -> None:
        is_correct: bool = option == self.level.correct
        guess: Guess = Guess(option, is_correct)
        self.guesses.append(guess)

        if not guess.is_correct and self.get_lives() == 0:
            self.game_over = True
            return

        self._next_level()

    def reset(self) -> None:
        self.game_over = False
        self.guesses = []
        self._next_level()

    def _next_level(self) -> None:
        self.level = Level.new_level(self.played_songs)
        self.played_songs.append(self.level.correct)

    def __repr__(self) -> str:
        result: str = ""
        for attr, attr_val in self.__dict__.items():
            result += f"{attr}: {attr_val}\n"
        return result
