import numpy as np

"""
A class representing artificial neural networks.
Design partly following:
Neural networks and deep learning, 2015
"""
class ANN():

    @staticmethod
    def sigmoid(zeta):
        """
        Activation function.
        """
        return 1. / (1. + np.exp(-zeta))

    @staticmethod
    def sigmoid_derivative(zeta):
        """
        Derivative of the activation function.
        """
        sigmoid0 = ANN.sigmoid(zeta)
        return sigmoid0 * (1. - sigmoid0)

    @staticmethod
    def cost(outputs, wanted):
        """
        Cross entropy cost function
        """
        return np.nan_to_num(np.sum(-wanted * np.log(outputs)
                                    -(1.-wanted) * np.log(1.-outputs)))

    @staticmethod
    def delta_error(outputs, wanted):
        """
        Error delta from the output layer.
        """
        return outputs - wanted


    def __init__(self, sizes):
        """
        The argument 'sizes' is a list of sizes of the neuron layers,
        i.e. [#inputs, #hidden1, #hidden2, ..., #outputs].
        """
        self.sizes = sizes
        self.num_layers = len(sizes)
        self.init_weights()

    def init_weights(self):
        """
        Initializes the weights and biases (index 0 of weights)
        """
        self.weights = []
        for layer in range(1, self.num_layers):
            weights = np.random.randn(self.sizes[layer], 
                                      1+self.sizes[layer-1])
            weights[:, 1:] /= np.sqrt(self.sizes[layer-1])
            self.weights.append(weights)

    def feedforward(self, activation):
        """
        Evaluate neuron outputs from the activation function.
        """
        for weights in self.weights:
            activation = np.insert(activation, 0, 1., axis=0)
            activation = ANN.sigmoid(np.dot(weights, activation))
        return activation

    def train1(self, inputs, wanted, learning_rate, regularization):
        """
        Train the network with online gradient descent (one input set).
        Arguments:
        - inputs: a data vector for the input layer
        - wanted: a correct output data vector
        - learning_rate: learning rate for the gradient descent method
        - regularization: the parameter in the regularization term
        """
        gradient_list = self.backpropagate(inputs, wanted)
        for layer in range(self.num_layers-1):
            self.weights[layer][1:] *= (1. - learning_rate * regularization)
            self.weights[layer] -= learning_rate * gradient_list[layer]

    def train_set(self, inputs, wanted, learning_rate, regularization,
        epochs, mini_batch_size, test_data=None):
        """
        Train the network with stochastic gradient descent.
        Arguments:
        - inputs: a list of data vectors for the input layer
        - wanted: a list of correct outputs data vector
        - learning_rate: learning rate for the gradient descent method
        - regularization: the parameter in the regularization term
        """
        n_samples = len(inputs)
        rand_inds = np.arange(n_samples)
        for ii in range(epochs):
            np.random.shuffle(rand_inds)
            for jj in range(0, n_samples, mini_batch_size):
                inds = rand_inds[jj: jj+mini_batch_size]
                inputs1 = [inputs[ind] for ind in inds]
                wanted1 = [wanted[ind] for ind in inds]
                self.train_minibatch(inputs1, wanted1,
                                     learning_rate, regularization/n_samples)

            print "Epoch {} trained.".format(ii)
            # test_data = [(x,y) for (x,y) in zip(inputs, wanted)]
            test_data = zip(inputs, wanted)
            if test_data:
                print "Evaluation: {0} / {1}".format(
                    self.evaluate(test_data), len(test_data))

    def evaluate(self, test_data):
        test_results = [(np.round(self.feedforward(x)), y) for (x,y) in test_data]
        return sum(x==y for (x,y) in test_results)

    def train_minibatch(self, inputs, wanted, learning_rate, regularization):
        """
        Train the network with stochastic gradient descent (mini batch).
        Arguments:
        - inputs: a list of data vectors for the input layer
        - wanted: a list of correct outputs data vector
        - learning_rate: learning rate for the gradient descent method
        - regularization: the parameter in the regularization term
        """
        gradient_list = [np.zeros(w.shape) for w in self.weights]
        for inputs1, wanted1 in zip(inputs, wanted):
            gradient_list1 = self.backpropagate(inputs1, wanted1)
            for layer in range(self.num_layers-1):
                gradient_list[layer][:] += gradient_list1[layer]

        for layer in range(self.num_layers-1):
            self.weights[layer][1:] *= (1. - learning_rate * regularization)
            self.weights[layer] -= learning_rate * gradient_list[layer] / len(inputs)

    def backpropagate(self, inputs, wanted):
        """
        Returns the gradient of the cost function.
        """

        # First feedforward
        activations = np.insert(inputs, 0, 1., axis=0)  # append one for bias term

        gradient_list = []
        activation_list = [activations]
        zeta_list = []

        for weights in self.weights:
            gradient_list.append(np.empty_like(weights))
            zeta = np.dot(weights, activations)
            zeta_list.append(zeta)
            activations = np.insert(ANN.sigmoid(zeta), 0, 1., axis=0)
            activation_list.append(activations)

        # Then backward pass, starting with the output layer
        delta = ANN.delta_error(activation_list[-1][1:], wanted)
        gradient_list[-1][:] = np.outer(delta, activation_list[-2].transpose())

        for layer in range(2, self.num_layers):
            spv = np.insert(ANN.sigmoid_derivative(zeta_list[-layer]), 0, 1., axis=0)
            delta = np.dot(self.weights[-layer+1].transpose(), delta) * spv
            gradient_list[-layer][:] = np.outer(delta[1:], activation_list[-layer-1].transpose())

        return gradient_list
