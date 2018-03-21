import random
import math
import copy
import numpy

"""
Represent an arbitrary neural network with fully-connected layers
(ie layer n is fully connected to layer n-1)
"""

class Network:
    def __init__(self, layer_sizes):
        self.layers = []
        self.edges = {}
        for size in layer_sizes:
            nodes = [0 for i in range(0, size)]
            self.layers.append(nodes)
        for i in range(0, len(self.layers) - 1):
            for j in range(0, len(self.layers[i])):
                for k in range(0, len(self.layers[i + 1])):
                    self.edges[(i, j, k)] = 0


    def get_edge(self, start_layer, start_node, end_node):
        return self.edges[(start_layer, start_node, end_node)]

    def set_input(self, input):
        #print self.layers[0]
        for i in range(0, len(input)):
            self.layers[0][i] = input[i]
        #print self.layers[0]

    def get_output(self):
        prev_outputs = self.layers[0]
        for l in range(1, len(self.layers)):
            curr_outputs = []
            for n in range(0, len(self.layers[l])):
                sum = self.layers[l][n] # sum starts off as the bias
                for m in range(0, len(prev_outputs)):
                    weight = self.get_edge(l - 1, m, n)
                    value = prev_outputs[m]
                    sum += weight * value
                curr_outputs.append(self.sigma(sum))
            prev_outputs = curr_outputs
        return prev_outputs

    def get_copy(self):
        copy_network = Network([])
        copy_network.layers = copy.deepcopy(self.layers)
        copy_network.edges = copy.deepcopy(self.edges)
        return copy_network

    # perturb the network with Guassian noise
    def perturb(self):
        xs = [] # array of random numbers drawn from a normal distribution
        weights_count = len(self.edges) # count of all manipulable weights/biases in the network
        for l in range(1, len(self.layers) - 1):
            weights_count += len(self.layers[l])
        for i in range(0, weights_count):
            xs.append(numpy.random.normal())
        k = 0.05 * (weights_count / sum([x**2 for x in xs]))**0.5 # normalization constant, as suggested by Oon and Henz (eq 3)
        # http://fileadmin.cs.lth.se/ai/Proceedings/aaai07/06/AAAI07-098.pdf
        weight_index = 0
        for l in range(1, len(self.layers) - 1):
            for n in range(0, len(self.layers[l])):
                self.layers[l][n] += k * xs[weight_index]
                weight_index += 1
        for edge in self.edges:
            self.edges[edge] += k * xs[weight_index]
            weight_index += 1

    # take the weighted average of self and other
    def weighted_average(self, other, weight):
        for l in range(0, len(self.layers)):
            for n in range(0, len(self.layers[l])):
                self.layers[l][n] = self.layers[l][n] * weight + other.layers[l][n] * (1 - weight)
        for edge in self.edges:
            self.edges[edge] = self.edges[edge] * weight + other.edges[edge] * (1 - weight)

    # write the network to a file
    def serialize(self, name):
        layers = open("networks/layers/%s.txt" % name, "wb+")
        layers.write(str(self.layers))
        layers.close()
        edges = open("networks/edges/%s.txt" % name, "wb+")
        edges.write(str(self.edges))
        edges.close()

    # read the network from a file
    def load(self, name):
        self.layers = eval(open("networks/layers/%s.txt" % name, "r").read())
        self.edges = eval(open("networks/edges/%s.txt" % name, "r").read())

    # sigmoid function
    def sigma(self, z):
        if z > 100:
            z = 100
        if z < -100:
            z = -100
        return 1.0 / (1.0 + math.exp(-z))
