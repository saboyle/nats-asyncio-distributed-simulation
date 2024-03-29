# Distributed Simulation [alpha/exploratory]

Example distributed simulation model for a two player / team adversarial game (e.g. Badminton, Tennis, Volleyball).

The model shows how a simulation can be implemented using asyncio and NATS.  (The abstraction also lends itself to 
implementation using actors i.e. Erlang, Akka).

The model chosen is deliberately simplistic, using only a single input parameter - server hold percentage.  It could be
made arbitrarily more sophisticated as needed.

The rules of the game are as follows:
* The game has two sides (teams or players)
* A match is made up of a number of games
* A game is made up of a number of points
* A game is won when a certain points threshold is reached
* A match is won when a certain number of games are won

## Inputs
* Number of simulations
* Server hold percentages for players A and B

## Outputs
* A 2-tuple of probabilities (team a (win), team b (win))

## Example implementation(s)
* Basic
    * Simulation is executed in a single thread, single process

* Parallel Multi-process
    * Simulation is executed across multiple processes
    
* Async / Non-blocking
    * Async scatter/gather implementation within a single event loop

* Distributed (using NATs + Docker) [Future e.g. https://github.com/saboyle/python-nats-pipeline-rest-gateway]
      
    * Queues are used as follows:
        * A simulation queue to hold queued simulation requests
        * A worker pulls a request and replies
        * The sim aggregates the replies from the reply queues and calculates output probabilities  
        
    * Processes
        * A simulator publishes simulation requests to the simulation queue
        * A simulation (Worker) listens to the simulation queue
        * An aggregator listens to the results queue
        
    * Scalability
        * Each process is implemented as a separate docker container
        * The simulations can be spread across multiple physical cores or machines as needed.
        * The degree of concurrency can be tuned by scaling the workers dynamically.

## Execution

**Note**: the [blocking wait] is to demonstrate how number of requests and amount of blocking affects execution time and
potential benefits of parallelization.

``` bash
Usage: python simulation.py [simulation size] [blocking wait]

python simulation.py 10000 0.001

{
  "conf": {
    "game_threshold": 3,
    "points_threshold": 21
  },
  "vars": {
    "a_hold_pct": 0.8,
    "b_hold_pct": 0.72,
    "first_server": "a"
  },
  "results": {
    "a_prob": 0.8768,
    "b_prob": 0.1232
  },
  "meta": {
    "iterations": 10000,
    "random_first_server": false
  }
}
```
    
## Notes

* The model calculates outcomes pre-match aka from an initialised gamestate although lends itself to easy enhancement to 
support modelling in-running.
* For simple models distribution is likely to slow execution, but complex models expectally those calling external 
services have potential benefits.
* The model provides some interesting data wrt the effect of knowing who will serve first in model accuracy.