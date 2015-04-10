import matplotlib.pyplot as plt

class Error_plot(object):
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(5,5))
        self.line1, = self.ax.semilogy([], [], 'r')
        self.line2, = self.ax.semilogy([], [], 'g')
        self.ax.set_xlim([0, 100])
        self.ax.set_ylim([1e-3, 10])
        self.ax.set_title('Cost')
        self.error1 = []
        self.error2 = []

        plt.draw()

    def update(self, err1, err2):
        self.error1.append(err1)
        self.error2.append(err2)

        self.line1.set_data(range(len(self.error1)), self.error1)
        self.line2.set_data(range(len(self.error2)), self.error2)
        plt.draw()