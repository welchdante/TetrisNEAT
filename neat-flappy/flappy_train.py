import neat
import pickle
import sys
from FlapPyBird.flappy import FlappyBirdApp

def neat_algorithm(n=20):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'flappy-config')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(False))
    winner = p.run(eval_genomes, n=n)
    pickle.dump(winner, open('winner.pkl', 'wb'))

def eval_genomes(genomes, config):
    idx, genomes = zip(*genomes)
    flappy_Bio = FlappyBirdApp(genomes, config)
    flappy_Bio.play()
    results = flappy_Bio.crash_info
    top_score = 0
    for result, genomes in results:
        score = result['score']
        distance = result['distance']
        energy = result['energy']
        fitness = score*3000 + 0.2*distance - energy*1.5
        genomes.fitness = -1 if fitness == 0 else fitness
        if top_score < score:
            top_score = score

    print('The top score was:', top_score)

def main():
    neat_algorithm()

if __name__ == "__main__":
	main()
