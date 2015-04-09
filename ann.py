import numpy as np

"""
A class representing artificial neural networks.
Currently supports feed-forward networks with one hidden layer.
"""
class ANN(object):

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
        Cross-entropy cost function
        """
        return np.nan_to_num(np.sum(-wanted * np.log(outputs)
                                    -(1. - wanted) * np.log(1. - outputs)))


    def __init__(self, n_input, n_hidden, n_output):
        self.sizes = (n_input, n_hidden, n_output)
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_output = n_output
        self.init_weights()
        
    def init_weights(self):
        """
        Initialize weights and biases for network connections.
        """
        self.hidden_bias = np.random.randn(self.n_hidden)
        self.hidden_weights = np.random.randn(self.n_hidden, self.n_input)
        self.hidden_weights /= np.sqrt(self.n_input)
        self.output_bias = np.random.randn(self.n_output)
        self.output_weights = np.random.randn(self.n_output, self.n_hidden)
        self.output_weights /= np.sqrt(self.n_hidden)

    def feedforward(self, inputs):
        """
        Activate inputs through the network.
        """
        hidden_activated = ANN.sigmoid(np.dot(self.hidden_weights, inputs)
                                       + self.hidden_bias)
        output_activated = ANN.sigmoid(np.dot(self.output_weights, hidden_activated)
                                       + self.output_bias)
        return output_activated

    def backpropagate(self, inputs, wanted):
        """
        Backpropagate the error in one input/output sample to get cost gradients.
        """
        hidden_zeta = np.dot(self.hidden_weights, inputs) + self.hidden_bias
        hidden_activated = ANN.sigmoid(hidden_zeta)
        output_zeta = (np.dot(self.output_weights, hidden_activated)
                       + self.output_bias)
        output_activated = ANN.sigmoid(output_zeta)

        delta_output = output_activated - wanted
        delta_hidden = (np.dot(self.output_weights.T, delta_output)
                        * ANN.sigmoid_derivative(hidden_zeta))

        output_cost_gradient_bias = delta_output
        output_cost_gradient_weight = np.outer(delta_output, hidden_activated)

        hidden_cost_gradient_bias = delta_hidden
        hidden_cost_gradient_weight = np.outer(delta_hidden, inputs)

        return [output_cost_gradient_bias, output_cost_gradient_weight,
                hidden_cost_gradient_bias, hidden_cost_gradient_weight]

    def train1(self, inputs, wanted, learning_rate, regularization):
        """
        Train the network with online gradient descent (one set of inputs).
        Arguments:
        - inputs: a data vector for the input layer
        - wanted: a correct output data vector
        - learning_rate: learning rate for the gradient descent method
        - regularization: the parameter in the regularization term
        """
        self.train_minibatch([inputs], [wanted], learning_rate, regularization)

    def train_minibatch(self, inputs_batch, wanted_batch, learning_rate,
                        regularization):
        """
        Train the network with stochastic gradient descent (mini batch).
        """

        gradients = self.backpropagate(inputs_batch[0], wanted_batch[0])
        for ii in range(1, len(inputs_batch)):
            gradients1 = self.backpropagate(inputs_batch[ii], wanted_batch[ii])
            for jj, grad in enumerate(gradients):
                gradients[jj] += grad

        self.output_bias -= learning_rate * gradients[0] / len(inputs_batch)
        # self.output_weights *= (1. - learning_rate * regularization)
        self.output_weights -= learning_rate * gradients[1] / len(inputs_batch)
        self.hidden_bias -= learning_rate * gradients[2] / len(inputs_batch)
        # self.hidden_weights *= (1. - learning_rate * regularization)
        self.hidden_weights -= learning_rate * gradients[3] / len(inputs_batch)

    def train_set(self, inputs_set, wanted_set, learning_rate, regularization,
        epochs, mini_batch_size):
        """
        Train the network with stochastic gradient descent.
        Arguments:
        - inputs_set: a list of data vectors for the input layer
        - wanted_set: a list of correct outputs data vector
        - learning_rate: learning rate for the gradient descent method
        - regularization: the parameter in the regularization term
        - epochs: passes through the training set
        - mini_batch_size: size of mini batches
        """
        n_samples = len(inputs_set)
        rand_inds = np.arange(n_samples)
        for ii in range(epochs):
            np.random.shuffle(rand_inds)
            for jj in range(0, n_samples, mini_batch_size):
                inds = rand_inds[jj: jj+mini_batch_size]
                inputs_batch = [inputs_set[ind] for ind in inds]
                wanted_batch = [wanted_set[ind] for ind in inds]
                self.train_minibatch(inputs_batch, wanted_batch,
                                     learning_rate, regularization/n_samples)
