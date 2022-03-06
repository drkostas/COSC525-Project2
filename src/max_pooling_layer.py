from src import Neuron
import numpy as np
from typing import *


class MaxPoolingLayer:
    def __init__(self, kernel_size: int, input_channels: int,
                 input_dimensions: Sequence[int]):
        """
        Initializes a max pooling layer.
        :param input_channels: Number of input channels (input width
        :param input_dimensions: Dimensions of input (height, width)
        """
        self.kernel_size = kernel_size
        self.input_dimensions = input_dimensions  # Dimensions of input (height, width)
        self.input_channels = input_channels  # Number of input channels
        self.neurons_per_layer = 0
        self.output_size = (input_dimensions[0] - kernel_size + 1,
                            input_dimensions[0] - kernel_size + 1)
        # Initialize neurons
        self.kernel = []  # Type:List[List[Neuron]]
        for neuron_ind_x in range(input_dimensions[0] - kernel_size + 1):
            neuron_row = []
            for neuron_ind_y in range(input_dimensions[1] - kernel_size + 1):
                neuron_weights = weights[kernel_ind, :]
                neuron = Neuron(num_inputs=kernel_size ** 2 * input_channels,
                                activation=self.activation,
                                lr=self.lr,
                                weights=neuron_weights,
                                input_channels=input_channels)
                neuron_row.append(neuron)
                self.neurons_per_layer = self.neurons_per_layer + 1
            self.kernel.append(neuron_row)

    def calculate(self, inputs: np.ndarray) -> np.ndarray:
        """
        Calculates the output of the layer.
        :param inputs: Inputs to the layer
        :return: Output of the layer
        """
        outputs = []
        for kernel_ind, kernel in enumerate(self.kernels):
            kernel_output = []
            for kernel_x, kernel_row in enumerate(kernel):
                kernel_x_output = []
                for kernel_y, neuron in enumerate(kernel_row):
                    if self.input_channels == 1:  # Shape is (kernel_size x kernel_size, )
                        inputs_to_neuron = inputs[kernel_x:kernel_x + self.kernel_size,
                                           kernel_y:kernel_y + self.kernel_size].reshape(-1)
                    else:  # Shape is (num_channels, kernel_size x kernel_size)
                        inputs_to_neuron = inputs[:,
                                           kernel_x:kernel_x + self.kernel_size,
                                           kernel_y:kernel_y + self.kernel_size] \
                            .reshape((self.input_channels, -1))
                    # Calculate output of each neuron
                    kernel_x_output.append(neuron.calculate(inputs_to_neuron))
                kernel_output.append(kernel_x_output)
            outputs.append(kernel_output)
        return np.array(outputs)

    def calculate_wdeltas(self, wdeltas_next: List) -> List:
        """
        Calculates the weight deltas of the layer.
        :param wdeltas_next: Weight deltas of the next layer
        :return: Weight deltas of the layer
        """
        wdeltas = []
        for ind, neuron in enumerate(self.neurons):
            # Calculate weight deltas of each neuron
            fwdelta = []
            for fwdeltas in wdeltas_next:
                fwdelta.append(fwdeltas[ind])
            fwdelta = np.sum(fwdelta)
            wdelta = neuron.calc_partial_derivative(fwdelta)
            # Update weights
            neuron.update_weights()
            wdeltas.append(wdelta)
        return wdeltas
