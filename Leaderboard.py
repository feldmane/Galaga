import os

class Leaderboard:

    max_scores = 10

    def __init__(self):
        self.scores = []
        self.dirty = False
        if not os.path.isfile("leaderboard.txt"):
            file = open("leaderboard.txt", "x")
            file.close()
        file = open("leaderboard.txt", "r")
        for line in file:
            score, initials = line.rstrip().split(":")
            self.scores.append((int(score), initials))

        if len(self.scores) < Leaderboard.max_scores:
            for i in range(Leaderboard.max_scores - len(self.scores)):
                self.scores.append((-1, ""))

        file.close()

    def get_scores(self):
        return self.scores

    def check_insert(self, score):
        return score > self.scores[len(self.scores) - 1][0]

    def insert_index(self, score):
        for i in range(len(self.scores)):
            if score > self.scores[i][0]:
                return i
        return -1

    def insert(self, score, initials=""):
        index = self.insert_index(score)
        if index >= 0:
            self.scores.insert(index, (score, initials))
            self.scores.pop()
            self.dirty = True
        return index

    def close(self):
        if self.dirty:
            file = open("leaderboard.txt", "w")
            for score in self.scores:
                if score[0] == -1:
                    continue
                file.write(str(score[0]) + ":" + str(score[1]))
                file.write("\n")
            file.close()
