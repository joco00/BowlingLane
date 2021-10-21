class Throw:
    """
    A data object that represents a throw
    Throw can be cast as a dict to obtain its state

    Attributes
    ----------
    data : 16 bit int
    frame : int
    pin_list: [int]
    pins_down: int

    Methods
    -------
    __iter__ -> yields attributes in a dictionary format
    """

    def __init__(self, data, frame, previousThrow=None) -> None:
        # get only the pins knocked down for this throw
        if previousThrow:
            data = data ^ previousThrow

        self.data = data
        self.frame = frame
        self.pin_list = [0 if 2 ** n & data == 0 else 1 for n in range(10)]
        self.pins_down = sum(self.pin_list)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return str(dict(self))

    def __iter__(self):
        yield "data", self.data
        yield "frame", self.frame
        yield "pins_down", self.pins_down
        yield "pin_list", self.pin_list


class Frame:
    """
    Represents a frame in a bowling match.
    Frame can be cast as a dict to obtain its state

    Attributes
    ----------
    throw1: Throw object
    throw2: Throw object
    isStrike: bool
    isSpare: bool
    score: int
    total_score: int
    frame_is_complete: bool


    Methods
    -------
    handleThrow -> none
    __iter__ -> (key, value)
    """

    def __init__(self):
        self.throw1 = None
        self.throw2 = None

        self.isStrike = False
        self.isSpare = False

        self.score = None
        self.total_score = None
        self.frame_is_complete = False

    def handleThrow(self, throw):
        """
        handleThrow processes a throw object, this can either be
        throw 1 or 2. The score for a spare or strike frame will NOT
        be handled in this function, it will be handled by the player
        object on later throws.

        :param throw: a throw object
        :return: none
        :side effects:
            sets throw objects
            sets score if not a strike or spare
            sets frame_is_complete

        """

        # first throw
        if not self.throw1:
            self.throw1 = throw
            if throw.pins_down == 10:
                self.isStrike = True
                self.frame_is_complete = True
                # scoring for strike happens 2 throws later
            return

        # second throw if needed
        self.throw2 = throw
        score = throw.pins_down + self.throw1.pins_down
        if score == 10:
            self.isSpare = True  # scoring for spare happens next throw
        else:
            self.score = score
        self.frame_is_complete = True

    # used to turn data into a dictionary and eventualy json
    def __iter__(self):
        yield "isStrike", self.isStrike
        yield "isSpare", self.isSpare
        yield "score", self.score
        yield "total_score", self.total_score
        yield "frame_is_complete", self.frame_is_complete
        yield "throw1", dict(self.throw1) if self.throw1 else None
        yield "throw2", dict(self.throw2) if self.throw2 else None

    def __repr__(self) -> str:
        return str(dict(self))


class Frame10(Frame):
    """
    Represents the 10th frame of a bowling match. Differs from Frame because frame 10
    needs to handle the case of a third throw
    """

    def __init__(self):
        super().__init__()
        self.throw3 = None

    def handleThrow(self, throw):
        """
        handleThrow processes a throw object, this can either be
        throw 1, 2, 3. The score for a spare or strike frame will NOT
        be handled in this function, it will be handled by the player
        object on later throws. This function acts a bit different as
        there can be a third throw if the frame is a strike or spare

        :param throw: a throw object
        :return: none
        :side effects:
            sets throw objects
            sets score if not a strike or spare
            sets frame_is_complete

        """
        if self.throw1 == None:
            self.throw1 = throw
            if self.throw1.pins_down == 10:
                self.isStrike = True

        elif self.throw2 == None:
            self.throw2 = throw

            # scoring for strike happens 2 throws later
            if self.isStrike:
                return

            pins_down = self.throw1.pins_down + self.throw2.pins_down
            if pins_down == 10:
                self.isSpare = True  # scoring for a spare happens on the next throw
            else:
                self.score = pins_down
                self.frame_is_complete = True

        else:
            self.throw3 = throw
            self.frame_is_complete = True

    def __iter__(self):

        for obj in super().__iter__():
            yield obj

        yield "throw3", dict(self.throw3) if self.throw3 else None


class Player:
    """
    Represents a player in a bowling match. Mangages 10 frames and handles
    throw data.

    Player can cast as a dict to obtain its state

    Attributes
    ----------
    name: str
    score: int
    throws: [Throw]
    frames: [Frame]
    current_frame: int
    callBack: Func
    reset: int
    secondThrow: int

    Methods
    -------
    handleThrow -> none
    checkReset -> none
    updateStrikesSpares -> none
    __iter__ -> (key,value)

    """

    def __init__(self, name, passedFunc):
        self.name = name
        self.score = 0

        self.throws = []
        self.frames = [Frame() for f in range(9)]
        self.frames.append(Frame10())

        self.current_frame = 0
        self.callBack = passedFunc

        self.reset = 2048
        self.secondThrow = 1024

    def handleThrow(self, data):
        """
        handleThrow processes incoming data, 16 bit int. A throw object
        will be created, stored, and then passed into the current frame object
        for furthur processing.

        :param data: 16 bit int
        :return: none
        :side effects: A lot
        """

        self.checkReset(data)

        # check if the data is a first or second throw, a second throw needs the previous
        # throws representation to calculate the pins it knocked down
        throw = (
            Throw(data, self.current_frame)
            if not (data & self.secondThrow)
            else Throw(data, self.current_frame, self.throws[-1].data)
        )
        self.throws.append(throw)
        self.updateStrikesSpares()

        current_frame = self.frames[self.current_frame]
        current_frame.handleThrow(throw)

        if current_frame.frame_is_complete:

            if not current_frame.isStrike and not current_frame.isSpare:
                self.score += current_frame.score
                current_frame.total_score = self.score

            self.current_frame += 1
            self.callBack()  # used to signal next player for the game object

    def checkReset(self, data):
        """
        checkReset processes incoming data, 16 bit int, to check for a reset
            removes any throws then resets the frame

        :param data: 16 bit int
        :return: none
        :side effects: resets the current frame, removes throws
        """
        if data & self.reset:
            if self.current_frame == 9 and not self.frames[9].frame_is_complete:
                if self.frames[self.current_frame].throw1:
                    self.throws.pop()
                if self.frames[self.current_frame].throw2:
                    self.throws.pop()
                self.frames[self.current_frame] = Frame10()
            else:
                if self.frames[self.current_frame].throw1:
                    self.throws.pop()
                self.frames[self.current_frame] = Frame()

    def updateStrikesSpares(self):
        """
        updateStrikesSpares updates the scores for unhandled strikes and spares

        :return: none
        :side effects: changes frame, and player scores
        """
        if len(self.throws) < 3:
            return

        throw = self.throws[-1]
        twoBackFrame = self.frames[self.throws[-3].frame]
        oneBackThrow = self.throws[-2]
        oneBackFrame = self.frames[oneBackThrow.frame]

        if twoBackFrame.isStrike:
            twoBackFrame.score = 10 + oneBackThrow.pins_down + throw.pins_down
            self.score += twoBackFrame.score
            twoBackFrame.total_score = self.score

        if oneBackFrame.isSpare:
            oneBackFrame.score = 10 + throw.pins_down
            self.score += oneBackFrame.score
            oneBackFrame.total_score = self.score

    def __iter__(self):
        yield "name", self.name
        yield "score", self.score
        yield "frames", [dict(f) for f in self.frames]

    def __str__(self) -> str:
        return self.__repr_()

    def __repr__(self) -> str:
        return str(dict(self))


class Game:
    """
    Represents the whole bowling match. Manages a list of players.
    Game can be cast as a dict to obtain its state

    Attributes
    ----------
    self.players: [Player]
    self.current_player: int
    self.frame_number: int
    self.total_frames: int
    self.game_is_over: bool
    self.turn_game_off: int

    Methods
    -------
    processInput -> None
    nextPlayer -> None
    setUpGame -> None
    __iter__ -> (key, value)
    """

    def __init__(self):
        self.players = []
        self.current_player = 0
        self.frame_number = 0
        self.total_frames = 0
        self.game_is_over = False
        self.turn_game_off = 4096

    def processInput(self, data):
        """
        processInput passes incoming data, 16 bit int, to the proper player object

        :param data: 16 bit int
        :return: none
        :side effects: A lot
        """
        if data & self.turn_game_off:
            self.game_is_over = True
            return

        self.players[self.current_player].handleThrow(data)

    def nextPlayer(self):
        """
        nextPlayer is used as a callback function from player objects.
        It increaments the frame number, and moves the current player
        to the next player in the list.


        :return: none
        :side effects: a lot
        """
        self.frame_number += 1

        if self.frame_number == self.total_frames:
            self.game_is_over = True

        self.current_player = (self.current_player + 1) % len(self.players)
        player = self.players[self.current_player]

    def setUpGame(self, names):
        """
        setUpGame creates the needed player objects and sets the number of
        frame in the game.

        :param names: [str] -> list of strings for players names
        :return: none
        :side effects:
            sets self.players
            sets self.total_frames
        """
        self.players = [Player(name, self.nextPlayer) for name in names]
        self.total_frames = len(self.players) * 10

    def __iter__(self):
        yield "players", [dict(p) for p in self.players]
