import neat
import pickle
import sys
from pprint import pprint
from FlapPyBird.flappy import FlappyBirdApp

def neat_algorithm(n=50):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'flappy-config')
    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(False))

    # Run until we achive n.
    winner = p.run(eval_genomes, n=n)

    pickle.dump(winner, open('winner.pkl', 'wb'))

def eval_genomes(genomes, config):

    # Play game and get results
    idx, genomes = zip(*genomes)
    
    flappy_Bio = FlappyBirdApp(genomes, config)
    flappy_Bio.play()
    results = flappy_Bio.crash_info    # Calculate fitness and top score
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
