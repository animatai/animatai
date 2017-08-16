Conceptual design
=================

Agents and Things live in a 2D environment. Agents are a type of Thing and there can
be many other types of Things, like Food, Obstacles etc. Agents can perceive Things
(including Agents). Agents that walk into Obstacles are bumped and stays in the previous
location.

Things are placed on top of the Terrain hiding the Terrain beneath it. The 
Terrain is showed again if a Thing is removed. Several Things can be in the same position,
with the exception of Obstalces (there cannot be any Things or Agents in the same place
as an Obstacle).

It is possible for Agents to pick up Things. These Things will then have the same
location until dropped.

There is also a Terrain but this is only used for rendering purposes. Agents cannot
percieve the Terrain.


Encoding of Terrain and Things
-----------------------------

These symbols are used in the Sea environment:

X: Obstalce (Thing)
W: Water (Terrain)
s: Squid (Thing)


An example world with Things and Terrain:

```
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WWWWssssWWWWWWWWWWWWWWWWWWWWWWWWWWWWssssWWWWWWWWWW
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WWWWssssWWWWWWWWWWWWWWWWWWWWWWWWWWWWssssWWWWWWWWWW
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
````

These are the Things:

```
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    ssss                            ssss         
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    ssss                            ssss         
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

And this is the Terrain:

```
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
```


