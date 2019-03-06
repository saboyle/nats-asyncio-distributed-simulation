import collections
import random
import logging
import json

Matchstate = collections.namedtuple('Gamestate', 'a_games b_games server')
Gamestate = collections.namedtuple('Gamestate', 'a_points b_points server')
Config = collections.namedtuple('config', 'game_threshold points_threshold')
Variables = collections.namedtuple('variables', 'a_hold_pct b_hold_pct first_server')
Results = collections.namedtuple('results', 'a_prob b_prob')

def _is_match_over(conf, matchstate):
    return (matchstate['a_games'] >= conf.game_threshold) or (matchstate['b_games'] >= conf.game_threshold)

def _is_game_over(conf, gamestate):
    return (gamestate['a_points'] >= conf.points_threshold) or (gamestate['b_points'] >= conf.points_threshold)

def _update_game_server(matchstate):
    logger.debug(f"End of game: new server, {matchstate['server']}, {matchstate}")
    if matchstate['server'] == 'a':
        matchstate['server'] = 'b'
    else:
        matchstate['server'] = 'a'
    return matchstate

def _update_point_server(gamestate, point_winner):
    """ Rally point scoring - winner of point becomes server """
    if gamestate['server'] == point_winner:
        logger.debug(f"Serve Held, {gamestate['server']}")
    else:
        if gamestate['server'] == 'a':
            logger.debug(f"Change of serve (next B), {gamestate}, {point_winner}")
            gamestate['server'] = 'b'
        else:
            logger.debug(f"Change of serve (next A), {gamestate}, {point_winner}")
            gamestate['server'] = 'a'
    return gamestate

def sim(conf, vars, iterations, random_first_server = False):
    logger.debug('================================')
    logger.debug("Simulation variables:")
    logger.debug('================================')
    logger.debug(sim_vars)
    logger.debug(sim_config)
    logger.debug('random first server:', random_first_server)
    logger.debug('================================')
    results = [sim_match(conf, vars, random_first_server) for r in range(iterations)]
    a_count = sum([1 for r in results if r['a_games'] > r['b_games']])
    b_count = sum([1 for r in results if r['a_games'] < r['b_games']])
    r = a_count / (a_count + b_count), b_count / (a_count + b_count)
    return Results(a_prob=r[0], b_prob=r[1])


def sim_match(conf, vars, random_first_server = False):
    if random_first_server:
        if random.random() > 0.5:
            server = 'a'
        else:
            server = 'b'
    else:
        server = vars.first_server

    matchstate = Matchstate(a_games=0, b_games=0, server=server)._asdict()
    while _is_match_over(conf, matchstate) == False:
        a_game_win = sim_game(conf, vars, matchstate['server'])
        if a_game_win:
            matchstate['a_games'] += 1
        else:
            matchstate['b_games'] += 1
        matchstate = _update_game_server(matchstate)
    return matchstate

def sim_game(conf, vars, first_server):
    gamestate = Gamestate(a_points=0, b_points=0, server=first_server)._asdict()
    while _is_game_over(conf, gamestate) == False:
        a_point_win = sim_point(gamestate, vars)
        if a_point_win:
            point_winner = 'a'
            gamestate['a_points'] += 1
            logger.debug('A wins point')
        else:
            point_winner = 'b'
            gamestate['b_points'] += 1
            logger.debug('B wins point')
        gamestate =_update_point_server(gamestate, point_winner)

    logger.debug('Game over')
    return gamestate['a_points'] > gamestate['b_points']

def sim_point(gamestate, vars):
    """ Team A wins the point - rally point scoring. """
    r = random.random()
    if gamestate['server'] =='a':
        return r <= vars.a_hold_pct
    else:
        return r >= vars.b_hold_pct


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    sim_config = Config(game_threshold=3, points_threshold=21)  # First to 3 games, with first to 21 points wins the game
    sim_vars = Variables(a_hold_pct=0.8, b_hold_pct=0.72, first_server='a')
    sim_iterations = 10000
    sim_random_first_server = False

    results = sim(sim_config, sim_vars, sim_iterations, random_first_server=sim_random_first_server)

    ret = {'conf': sim_config._asdict(), 'vars': sim_vars._asdict(), 'results': results._asdict(),
           'meta': {'iterations': sim_iterations, 'random_first_server': sim_random_first_server}}
    print(json.dumps(ret, indent=2))

