import multiprocessing
from functools import partial
import random
import logging
import json
import time

class Matchstate(object):
    def __init__(self, a_games, b_games, server):
        self.a_games = a_games
        self.b_games = b_games
        self.server = server

    def __repr__(self):
        return json.dumps(self.__dict__)

class Gamestate(object):
    def __init__(self, a_points, b_points, server):
        self.a_points = a_points
        self.b_points = b_points
        self.server = server

    def __repr__(self):
        return json.dumps(self.__dict__)

class Config(object):
    def __init__(self, game_threshold, points_threshold):
        self.game_threshold = game_threshold
        self.points_threshold = points_threshold

    def __repr__(self):
        return json.dumps(self.__dict__)

class Variables(object):
    def __init__ (self, a_hold_pct, b_hold_pct, first_server):
        self.a_hold_pct = a_hold_pct
        self.b_hold_pct = b_hold_pct
        self.first_server = first_server

    def __repr__(self):
        return json.dumps(self.__dict__)

class Results(object):
    def __init__(self, a_prob, b_prob):
        self.a_prob = a_prob
        self.b_prob = b_prob

    def __repr__(self):
        return json.dumps(self.__dict__)

def _is_match_over(conf, matchstate):
    return (matchstate.a_games >= conf.game_threshold) or (matchstate.b_games >= conf.game_threshold)

def _is_game_over(conf, gamestate):
    return (gamestate.a_points >= conf.points_threshold) or (gamestate.b_points >= conf.points_threshold)

def _update_game_server(matchstate):
    logger.debug(f"End of game: new server, {matchstate.server}, {matchstate}")
    if matchstate.server == 'a':
        matchstate.server = 'b'
    else:
        matchstate.server = 'a'
    return matchstate

def _update_point_server(gamestate, point_winner):
    """ Rally point scoring - winner of point becomes server """
    if gamestate.server == point_winner:
        logger.debug(f"Serve Held, {gamestate.server}")
    else:
        if gamestate.server == 'a':
            logger.debug(f"Change of serve (next B), {gamestate}, {point_winner}")
            gamestate.server = 'b'
        else:
            logger.debug(f"Change of serve (next A), {gamestate}, {point_winner}")
            gamestate.server = 'a'
    return gamestate


def sim(conf, vars, iterations, random_first_server = False):
    logger.info('================================')
    logger.info("Simulation variables:")
    logger.info('================================')
    logger.info(sim_vars)
    logger.info(sim_config)
    logger.info(f"random first server:, {random_first_server}")
    logger.debug('================================')

    # results = [sim_match(conf, vars, random_first_server) for r in range(iterations)]

    fun = partial(sim_match, conf, vars, random_first_server)
    with multiprocessing.Pool() as pool:
        results = pool.map(fun, list(range(iterations)))

    a_count = sum([1 for r in results if r.a_games > r.b_games])
    b_count = sum([1 for r in results if r.a_games < r.b_games])

    r = a_count / (a_count + b_count), b_count / (a_count + b_count)
    res = Results(a_prob=r[0], b_prob=r[1])
    # logger.info(f"output probabilities: {json.dumps(res)}")
    return res


def sim_match(conf, vars, random_first_server, sim_id):
    time.sleep(DELAY)
    if random_first_server:
        if random.random() > 0.5:
            server = 'a'
        else:
            server = 'b'
    else:
        server = vars.first_server

    matchstate = Matchstate(a_games=0, b_games=0, server=server)
    while _is_match_over(conf, matchstate) == False:
        a_game_win = sim_game(conf, vars, matchstate.server)
        if a_game_win:
            matchstate.a_games += 1
        else:
            matchstate.b_games += 1
        matchstate = _update_game_server(matchstate)
    return matchstate


def sim_game(conf, vars, first_server):
    gamestate = Gamestate(a_points=0, b_points=0, server=first_server)
    while _is_game_over(conf, gamestate) == False:
        a_point_win = sim_point(gamestate, vars)
        if a_point_win:
            point_winner = 'a'
            gamestate.a_points += 1
            logger.debug('A wins point')
        else:
            point_winner = 'b'
            gamestate.b_points += 1
            logger.debug('B wins point')
        gamestate =_update_point_server(gamestate, point_winner)

    logger.debug('Game over')
    return gamestate.a_points > gamestate.b_points

def sim_point(gamestate, vars):
    """ Team A wins the point - rally point scoring. """
    r = random.random()
    if gamestate.server =='a':
        return r <= vars.a_hold_pct
    else:
        return r >= vars.b_hold_pct


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:
        print("Usage python simulation.py [num_iterations] [delay]")
        exit(0)
    else:
        sim_iterations = int(sys.argv[1])
        sim_delay = float(sys.argv[2])

    DELAY = sim_delay

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.ERROR)

    sim_config = Config(game_threshold=3, points_threshold=21)  # First to 3 games, with first to 21 points wins the game
    sim_vars = Variables(a_hold_pct=0.8, b_hold_pct=0.72, first_server='a')
    sim_random_first_server = False

    results = sim(sim_config, sim_vars, sim_iterations, random_first_server=sim_random_first_server)

    ret = {'conf': sim_config, 'vars': sim_vars, 'results': results,
           'meta': {'iterations': sim_iterations, 'random_first_server': sim_random_first_server}}
    print(ret)

