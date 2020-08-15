# Social Network User Credibility

## About

The project simulates a social network and optimizes an algorithm described here[0].

## Running

The code requires python (3.8+) and uses the graph library [NetworkX](https://networkx.github.io/) (2.4+).

In order to run:

```bash
$ pip install matplotlib networkx
$ python social-network-credibility.py
```

## Example

```
$ python social-network-credibility.py
Insert the requested amount of users: 30 # amount of users in social network
Insert the requested amount of friendships: 50 # amount of friendships, they are randomly distributed among users
Insert the requested MSP: 0.5 # 0 to 1 threshold for credibility
.
. # a plot of the social network graph
.
Insert the requested source node: 4
Insert the requested target node: 9
.
. # a plot of the resulting path between the source and the target, if it exists
.
```

[0] Gudes Ehud and Nadav Voloch - "An Information-Flow Control Model
for Online Social Networks Based on User-Attribute Credibility and
ConnectionStrength Factors". International Symposium on Cyber
Security Cryptography and Machine Learning. Springer, Cham, 2018.
