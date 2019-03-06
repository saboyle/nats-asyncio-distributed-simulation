# Distributed Simulation

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
* A list of completed match outcomes.
* For each outcome the final score in games as a tuple.

## Example implementation(s)
* Basic
    * Simulation is executed in a single thread, single process
* Multi-process
    * Simulation is executed across multiple processes
* Distributed (using NATs + Docker)
      
    * Two queues are used:
        * A simulation queue to hold queued simulation requests
        * A results queue to hold output match results
        
    * Processes
        * A simulation (Worker) listens to the simulation queue
        * An aggregator listens to the results queue
        
     * Scalability
        * Each process is implemented as a separate docker container
        * The simulations can be spread across multiple physical cores or machines as needed.
        * The degree of concurrency can be tuned by scaling the workers dynamically.
    
## Notes

* The model calculates outcomes pre-match aka from an initialised gamestate although lends itself to easy enhancement to 
support modelling in-running.
* For simple models distribution is likely to slow execution, but complex models expectally those calling external 
services have potential benefits.
* The model provides some interesting data wrt the effect of knowing who will serve first in model accuracy.