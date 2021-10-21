from game import *
from laneController import LaneConnector
from scoreBoardController import ScoreBoardController


class Lane:
    """
    Root object for this application.

    Attributes
    ----------
    sbc: ScoreBoardController
    lc: LaneConnector
    game: Game

    Methods
    -------
    turnOnLane -> None
    """

    def __init__(self):
        self.sbc = ScoreBoardController()
        self.lc = LaneConnector()
        self.game = Game()

    def turnOnLane(self):
        """
        turnOnLane starts a bowling game

        :return: none
        :side effects: a lot
        """

        # i image that the player names come from the score baord
        self.game.setUpGame(self.sbc.getPlayerNames())

        while not self.game.game_is_over:
            self.game.processInput(self.lc.getInput())
            self.sbc.displayGame(dict(self.game))
