import math

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = []
        self.token_map = {}

    def add_token(self, index, name):
        self.token_map[index] = name

    def add_edge(self, source, target, rate):
        weight = -math.log(rate)
        self.graph.append([source, target, weight])

    def arbitrage(self, source):
        distance = [float("Inf")] * self.V
        distance[source] = 0
        prev = [0] * self.V  # To keep track of the path

        for _ in range(self.V - 1):
            for source, target, weight in self.graph:
                if distance[source] != float("Inf") and distance[source] + weight < distance[target]:
                    distance[target] = distance[source] + weight
                    prev[target] = source  # Keep track of the path

        for source, target, weight in self.graph:
            if distance[source] != float("Inf") and distance[source] + weight < distance[target]:
                print("Arbitrage opportunity detected: ")
                print("Buy", self.token_map[source])
                path = [target]
                while target != source:
                    path.insert(0, prev[target])
                    target = prev[target]
                path.append(source)
                for i in range(len(path) - 1):
                    print("Trade", self.token_map[path[i]], "for", self.token_map[path[i+1]])
                return
        print("No arbitrage opportunity detected")

g = Graph(3)
g.add_token(0, "ETH")
g.add_token(1, "DAI")
g.add_token(2, "USDT")
g.add_edge(0, 1, 2004)  # ETH -> DAI
g.add_edge(1, 0, 0.0004)  # DAI -> ETH
g.add_edge(1, 2, 1)  # DAI -> USDT
g.add_edge(2, 1, 1)  # USDT -> DAI
g.add_edge(0, 2, 2002)  # ETH -> USDT
g.add_edge(2, 0, 0.0008)  # USDT -> ETH

g.arbitrage(0)
