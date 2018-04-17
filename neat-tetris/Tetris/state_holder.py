from Tetris.tetris import Tetris

class StateHolder(object):
    def __init__(self, genomes, config):

        self.agents = [Tetris(genome, config) for genome in genomes]
        self.score = 0
        self.game_end_info = []

    def play(self):
        for game in self.agents:
            result = game.run()
            self.game_end_info.append(result)

