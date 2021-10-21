import os


class ScoreBoardController:
    """
    Used to visually display a bowling game in formatted text.

    I imagined input as being in json format. Maybe the game state
    is run on server then updates the display by sending data is json format.
    This is a text implementation instead of a graphical one for simplicity.



    Attributes
    ----------
    None

    Methods
    -------
    getPlayerNames -> [str]
    displayGame -> None
    displayPlayer ->None
    displayData -> None
    createFrame -> [str]
    createFrame10 -> [str]
    """

    def __init__(self):
        pass

    def getPlayerNames(self):
        """
        getPlayerNames obtains a list of strings from stdin

        :return: [str]
        """

        print("How many players: ")
        inpt = input()

        while (not inpt.isnumeric()) or int(inpt) < 1:
            inpt = input()

        return [input() for n in range(int(inpt))]

    def displayGame(self, data):
        """
        displayGame prints to stdout the game state.

        :param data: {} that contains the game data
        :return: None
        """

        self.storeData(data)

        os.system("clear")
        print("---------------------------------------------------------")
        print("|name|| 1 || 2 || 3 || 4 || 5 || 6 || 7 || 8 || 9 || 10  |")
        print("---------------------------------------------------------")
        for p in data["players"]:
            self.displayPlayer(p)

    def displayPlayer(self, player):
        """
        displayPlayer prints to stdout the a players score line

        :param player: {} that contains the player data
        :return: None
        """

        str_frame = [
            f"|{ (player['name']+ '   ' )[0:4]}|",
            f"|    |",
            "-----",
        ]

        for num, f in enumerate(player["frames"]):
            frm = self.createFrame(num, f)
            str_frame[0] += frm[0]
            str_frame[1] += frm[1]
            str_frame[2] += frm[2]

        for s in str_frame:
            print(s)

    def createFrame(self, num, frame):
        """
        createFrame prints to stdout the a players score line

        :param num: int that represents the frame number
        :param frame: {} that contains the frame data
        :return: [str]
        """

        if num == 9:
            return self.createFrame10(frame)

        t1 = " "
        t2 = " "
        score = str(frame["total_score"]) if frame["total_score"] else "   "
        score = " " * (3 - len(score)) + score

        if frame["isStrike"]:
            t2 = "X"
            t1 = " "
        elif frame["isSpare"]:
            t1 = frame["throw1"]["pins_down"]
            t2 = "/"
        else:
            if frame["throw1"]:
                t1 = frame["throw1"]["pins_down"]
            if frame["throw2"]:
                t2 = frame["throw2"]["pins_down"]

        return [f"|{t1}|{t2}|", f"|{score}|", "-----"]

    def createFrame10(self, frame):
        t1 = " "
        t2 = " "
        t3 = " "

        score = str(frame["total_score"]) if frame["total_score"] else "   "
        score = " " * (3 - len(score)) + score

        if frame["throw1"]:
            pd = frame["throw1"]["pins_down"]
            if pd == 10:
                t1 = "X"
            else:
                t1 = pd

        if frame["throw2"]:
            pd = frame["throw2"]["pins_down"]
            if t1 == "X":
                if pd == 10:
                    t2 = "X"
                else:
                    t2 = pd
            elif frame["throw1"]["pins_down"] + pd == 10:
                t2 = "/"
            else:
                t2 = pd
                t3 = "-"

        if frame["throw3"]:
            pd = frame["throw3"]["pins_down"]
            if pd == 10:
                t3 = "X"
            else:
                t3 = pd

        return [f"|{t1}|{t2}|{t3}|", f"| {score} |", "-------"]

    def storeData(self, data):
        """
        storeData writes data to the file data.json

        :param data: {} that contains the game data
        :return: None
        """

        import json

        with open("data.json", "w") as outfile:
            json.dump(data, outfile)
