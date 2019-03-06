import collections
import random

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
    if matchstate['server'] == 'a':
        matchstate['server'] = 'b'
    else:
        matchstate['server'] = 'a'

def _update_point_server(gamestate, point_winner):
    """ Rally point scoring - winner of point becomes server """
    if gamestate['server'] == point_winner:
        pass
    else:
        if gamestate['server'] == 'a':
            gamestate['server'] == 'b'
        else:
            gamestate['server'] = 'a'

def sim(conf, vars, iterations, random_first_server = False):
    print('================================')
    print("Simulation variables:")
    print('================================')
    print(sim_vars)
    print(sim_config)
    print('random first server:', random_first_server)
    print('================================')
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
        _update_game_server(matchstate)
    return matchstate

def sim_game(conf, vars, first_server):
    gamestate = Gamestate(a_points=0, b_points=0, server=first_server)._asdict()
    while _is_game_over(conf, gamestate) == False:
        a_point_win = sim_point(gamestate, vars)
        if a_point_win:
            gamestate['a_points'] += 1
        else:
            gamestate['b_points'] += 1
    return gamestate['a_points'] > gamestate['b_points']

def sim_point(gamestate, vars):
    """ Team A wins the point - rally point scoring. """
    r = random.random()
    if gamestate['server'] =='a':
        return r <= vars.a_hold_pct
    else:
        return r >= vars.b_hold_pct


if __name__ == "__main__":
    sim_config = Config(game_threshold=3,
                        points_threshold=21)  # First to 3 games, with first to 21 points wins the game
    sim_vars = Variables(a_hold_pct=0.7, b_hold_pct=0.6, first_server='a')

    print(sim(sim_config, sim_vars, 10000, random_first_server=True))
