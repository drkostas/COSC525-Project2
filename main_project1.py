import traceback
import argparse
import numpy as np
from src import NeuralNetwork
from typing import *


def get_args() -> argparse.Namespace:
    """Set-up the argument parser

    Returns:
        argparse.Namespace:
    """
    parser = argparse.ArgumentParser(
        description='Project 1 for the Deep Learning class (COSC 525). '
                    'Involves the development of a Feed-Forward Neural Network.',
        add_help=False)
    # Required Args
    required_args = parser.add_argument_group('Required Arguments')
    required_args.add_argument('-d', '--dataset', required=True,
                               help="The datasets to train the network on. "
                                    "Options: [and, xor, class_example]")
    required_args.add_argument('-n', '--network', required=True,
                               help="The network configuration to use. "
                                    "Options: [1x1_net, 2x1_net, 2x2_net]")
    # Optional args
    optional_args = parser.add_argument_group('Optional Arguments')
    optional_args.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    return parser.parse_args()


def get_network_config(network_name: str) -> Dict[str, Any]:
    """Get the network configuration

    Args:
        network_name (str): The name of the network to get the configuration for

    Returns:
        Dict[str, Any]: The network configuration
    """
    nn_conf = {}
    if network_name == '1x1_net':
        nn_conf['neurons_per_layer'] = [1]
        nn_conf['activations'] = ['logistic']
        nn_conf['loss_function'] = 'square_error'
        nn_conf['learning_rate'] = 5
        nn_conf['epochs'] = 5000
        nn_conf['print_every'] = 500
    elif network_name == '2x1_net':
        nn_conf['neurons_per_layer'] = [2, 1]
        nn_conf['activations'] = ['logistic', 'logistic']
        nn_conf['loss_function'] = 'square_error'
        nn_conf['learning_rate'] = 5
        nn_conf['epochs'] = 5000
        nn_conf['print_every'] = 500
    elif network_name == '2x2_net':
        nn_conf['neurons_per_layer'] = [2, 2]
        nn_conf['activations'] = ['logistic', 'logistic']
        nn_conf['loss_function'] = 'cross_entropy'
        nn_conf['learning_rate'] = 0.5
        nn_conf['epochs'] = 100
        nn_conf['print_every'] = 100
    else:
        raise ValueError(f"Network name {network_name} not recognized.")

    return nn_conf


def get_dataset_config(dataset_name: str) -> Dict[str, Any]:
    """Get the dataset configuration

    Args:
        dataset_name (str): The name of the dataset to get the configuration for

    Returns:
        Dict[str, Any]: The dataset configuration
    """
    dataset_conf = {}
    if dataset_name == 'and':
        dataset_conf['inputs'] = [[0, 0], [0, 1], [1, 0], [1, 1]]
        dataset_conf['outputs'] = [[0], [0], [0], [1]]
    elif dataset_name == 'xor':
        dataset_conf['inputs'] = [[0, 0], [0, 1], [1, 0], [1, 1]]
        dataset_conf['outputs'] = [[0], [1], [1], [0]]
    elif dataset_name == 'class_example':
        dataset_conf['inputs'] = [0.05, 0.1]
        dataset_conf['desired_outputs'] = [0.01, 0.99]
        dataset_conf['weights'] = [[[0.15, 0.20, 0.35], [0.25, 0.30, 0.35]],
                                   [[0.40, 0.45, 0.60], [0.50, 0.55, 0.60]]]
    else:
        raise ValueError(f"Dataset name {dataset_name} not recognized.")

    return dataset_conf


def main():
    """This is the main function of main.py

    Example:
        python main.py --dataset xor --network 2x1_net
    """

    # Initializing
    args = get_args()
    # Load the configurations
    nn_type = args.network
    nn_conf = get_network_config(nn_type)
    dataset_type = args.dataset
    dataset_conf = get_dataset_config(dataset_type)

    # ------- Start of Code ------- #
    print()
    print(f'Training the `{nn_type}` network on the `{dataset_type}` dataset.')
    if args.dataset != 'class_example':  # XOR and AND cases
        # Train the network
        inputs = np.array(dataset_conf['inputs'])
        outputs = np.array(dataset_conf['outputs'])
        # Initialize the network
        netWork = NeuralNetwork(input_size=inputs.shape[1],
                                loss_function=nn_conf['loss_function'],
                                learning_rate=nn_conf['learning_rate'])
        # Add the layers
        for num_neurons, activation in zip(nn_conf['neurons_per_layer'], nn_conf['activations']):
            netWork.addFCLayer(num_neurons=num_neurons, activation=activation)
        # Train the network for the given number of epochs
        for epoch in range(nn_conf['epochs']):
            netWork.train(inputs, outputs)  # Train the network
            loss = netWork.calculate_loss(inputs, outputs)  # Calculate the loss
            if epoch % nn_conf['print_every'] == 0:
                print(f"Epoch: {epoch} Loss: {loss}")
        print(f"Epoch: {nn_conf['epochs']} Loss: {loss}")
        # Test on the predictions
        print(f'Predictions on the {dataset_type} dataset')
        for inp, outp in zip(inputs, outputs):
            print(f"True Output: {outp} Prediction: {netWork.calculate(inp)[0]}")
    else:  # Class Example
        # Set up the weights and biases based on the class example
        inputs = [np.array(dataset_conf['inputs'])]
        desired_outputs = np.array(dataset_conf['desired_outputs'])
        weights = [np.array(weight) for weight in dataset_conf['weights']]
        # Initialize the network using the predefined weights and biases
        netWork = NeuralNetwork(input_size=2,
                                loss_function=nn_conf['loss_function'],
                                learning_rate=nn_conf['learning_rate'])
        # Add the layers
        for num_neurons, activation, weights_ in \
                zip(nn_conf['neurons_per_layer'], nn_conf['activations'], weights):
            netWork.addFCLayer(num_neurons=num_neurons, activation=activation,
                               weights=weights_)
        # Print the network inputs and weights before training
        print("Pre-training Inputs:")
        print(f"{inputs[0]}")
        print("Pre-training Weights:")
        print(f"{netWork.layers[0].neurons[0].weights} (h1) x "
              "{netWork.layers[1].neurons[0].weights} (O1)")
        print(f"{netWork.layers[0].neurons[1].weights} (h1) x "
              "{netWork.layers[1].neurons[1].weights} (O1)")
        # Activate the network
        outputs = netWork.calculate(inputs[0])  # Feed-forward the network
        print(f"Outputs after calling `activate()`:")
        print(f"{outputs}")
        # Calculate the wdeltas - single step of backpropagation
        wdeltas = [netWork.loss_derivative(np.array(outputs), desired_outputs)]
        for j in range(len(netWork.layers) - 1, -1, -1):
            wdeltas = netWork.layers[j].calculate_wdeltas(wdeltas)
        # Print the wdeltas, the weights, and the outputs after backpropagation
        print("Wdeltas after calling `calculate_wdeltas()`:")
        print(f"{wdeltas}")
        print("Weights after a single step of back-propagation:")
        print(f"{netWork.layers[0].neurons[0].weights} (h1) x "
              "{netWork.layers[1].neurons[0].weights} (O1)")
        print(f"{netWork.layers[0].neurons[1].weights} (h1) x "
              "{netWork.layers[1].neurons[1].weights} (O1)")
        outputs = netWork.calculate(inputs[0])
        print("Post-training Outputs:")
        print(f"{outputs}")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(str(e) + '\n' + str(traceback.format_exc()))
        raise e
