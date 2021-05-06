# Machine learning chess application using self-play for reinforcement
Utilizing the framework from AlphaZero research papers, this is an implementation of a self-play machine learning chess machine using a convolutional neural network (CNN) with skip connections
(Residual Network) and Monte Carlo tree search to self-play and learn. Project contains a GUI for human vs. human play, human vs network play, and visualization of self-play while the network is
learning.

# Outline of files
`Game.py`
This file contains the programmed rules of the game (chess) and a class to create the game object. The game state (color to move, move number, board state, etc) is stored and updated 
as moves are completed. If using the GUI, legal moves are highlighted when a piece is picked up.
This file also contains functions for encoding the current game and board state, along with move history, for input into the network. One-hot encodings are used for encoding game and board state features. 

`Gui.py`
This file uses PyGame to produce a graphical user interface for user visualization. If the gui variable is set to true, when this file is run it instantiates a new game and allows for a normal game of chess to be played. This can also be used to visualize the moves played by the network during self-play.

`Network.py`
Using Keras, this is a very simple convolutional network of only a few layers to show the layout and ability to save a network in a local repository.

`Resnet.py`
Also using Keras, this is a much more in depth convolutional neural network utlizing skip connections for deeper network learning. Setup in the same way as Network.py, this allows the user to save the model, as well as load the saved model, in the local repository.

`Learning.py`
This is the main file for training and self-play of the neural network. When called, this loads in the locally saved network model and instantiates a Game object. Through the use of a monte carlo tree search and initially randomized values of initial moves, the network plays through a game, selecting moves based on network output values, then updating the trainable wieghts within the network with a function designed to reduce the error between expected output value of the game for a given move with the observed actual outcome of the game at the end of the self play simulation.
Using the config class at the top of the Learning.py file, users can alter the number of simulations run, moves per simulation, and network learning fields. While running, Learning.py will output to console information regarding the self play (Game #, simulation #, move #, etc). 
View the bottom of this file for varying ways to run self-play.


