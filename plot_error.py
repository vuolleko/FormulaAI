import matplotlib.pyplot as plt

import constants

class Error_plot(object):
    """
    This class adds a plot of the evolving values
    of the cost function for each car.
    """
    def __init__(self, cars):
        self.cars = cars
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(5,5))
        self.lines = []
        self.errors = []
        self.mean_errors = []
        self.xpos = []

        for car in cars:
            # car colors are in range [0, 255]; must be normalized for pyplot
            color = []
            for comp in car.color:
                color.append(comp / 255.)

            self.lines.append(*self.ax.semilogy([], [], color=color,
                                                label=car.name))
            self.errors.append([])
            self.mean_errors.append([])

        self.ax.set_xlim([0, 180])
        self.ax.set_ylim([1e-2, 10])
        self.ax.set_ylabel('Cost function')
        self.ax.set_xlabel('Time [s]')
        self.ax.legend()

        plt.draw()

    def update(self, frame_counter):
        """
        Update error data and plot.
        """
        for ii, car in enumerate(self.cars):
            self.errors[ii].append(car.driver.error)

        if frame_counter % constants.PLOT_ERROR_INTERVAL == 0:
            self.xpos.append(frame_counter / constants.FRAME_RATE)

            for ii, car in enumerate(self.cars):
                self.mean_errors[ii].append(mean(self.errors[ii]))
                self.errors[ii] = []
                self.lines[ii].set_data(self.xpos, self.mean_errors[ii])

            plt.draw()


def mean(data):
    """
    Calculate the arithmetic mean of data.
    """
    if len(data) == 0:
        return 0.
    data_sum = 0.
    for sample in data:
        data_sum += sample
    return data_sum / len(data)
