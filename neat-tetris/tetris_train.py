import neat
import pickle
from Tetris.state_holder import StateHolder

def neat_algorithm(n=500):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'tetris-config')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(False))
    winner = p.run(eval_genomes, n=n)
    pickle.dump(winner, open('winner2.pkl', 'wb'))

def eval_genomes(genomes, config):
    idx, genomes = zip(*genomes)
    tetris_agents = StateHolder(genomes, config)
    tetris_agents.play()
    results = tetris_agents.game_end_info
    for result, genomes in results:
        score = result['score']
        holes = result['holes']
        bumpiness = result['bumpiness']
        aggregate_height = result['aggregate_height']
        fitness = (0.1 * score) - (.03*bumpiness) - (.2*holes) - (.01 * aggregate_height)
        genomes.fitness = fitness

def main():
    neat_algorithm()

if __name__ == "__main__":
    main()