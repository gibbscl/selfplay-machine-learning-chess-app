import tensorflow as tf
from tensorflow import keras
from game import Game
import math, numpy, copy, time



class Config():
    total_move_number = 4864
    max_moves = 50
    #num_sample_moves = 30
    num_simulations = 100

    # Root prior exploration noise.
    root_dirichlet_alpha = 0.3  
    root_exploration_fraction = 0.25

    pb_c_base = 19652
    pb_c_init = 1.25

    training_steps = 10
    checkpoint_interval = 2
    window_size = 1000
    batch_size = 50

    weight_decay = 1e-4
    momentum = 0.9
    learning_rate = 0.2

    learning_rate_schedule = {
        0: 2e-1,
        100e3: 2e-2,
        300e3: 2e-3,
        500e3: 2e-4
    }


class Network(object):
    def __init__(self):
        self.model = keras.models.load_model(".\model")

    def save(self):
        self.model.save('.\model')

    def predict(self, input):
        output = network.model.predict(input)
        policy_output, value_output = output[0][0], output[1][0][0]
        return policy_output, value_output

    def get_weights(self):
        return self.model.get_weights()


class Node(object):
    def __init__(self, prior):
        self.prior = prior
        self.visit_count = 0
        self.value_sum = 0
        self.children = {}
        self.child_visits = []
        self.color_to_move = None
    
    def value(self):
        if self.visit_count == 0:
            return 0
        return self.value_sum / self.visit_count
    
    def expanded(self):
        return self.children != {}

    
class Storage(object):
    def __init__(self):
        self.buffer = []
        self.networks = {}
        self.batch_size = 1

    def save_game(self, game):
        if len(self.buffer) > Config.window_size:
            self.buffer.pop(0)
            self.buffer.append(game)
        else:
            self.buffer.append(game)

    def sample_batch(self):
    # Sample uniformly across positions.
        move_sum = float(sum(len(game.history) for game in self.buffer))
        games = numpy.random.choice(
            self.buffer,
            size=self.batch_size,
            p=[len(game.history) / move_sum for game in self.buffer])
        game_pos = [(game, numpy.random.randint(len(game.history))) for game in games]
        return [(game.make_image(i), game.make_target(i)) for (game, i) in game_pos]

    def save_network(self, step, network):
        self.networks[step] = network
    

def simulate_game(network, game_count):
    game = Game()
    move_count = 1
    print('Starting Game ' + str(game_count))
    #While the game is still ongoing, run the MCTS, finding a new move
    while game.status == None and game.full_move_count < Config.max_moves:
        t0 = time.perf_counter()
        next_move, root = mcts(network, game, game_count, move_count)
        #Executing the found move in the current game
        game.execute_move(next_move)
        move_count+=1
        t1 = time.perf_counter()
        print('    Executing Move ' + str(game.full_move_count) + ' for game ' + str(game_count) + 
        ' (' + str(round(t1 - t0,2)) + ' seconds)')
        game.update_stats(root)

    return game


def mcts(network, game, game_count, move_count):
    root = Node(0)
    evaluate(network, game, root)
    add_exploration_noise(root)
    root.color_to_move = game.color_to_move

    #Running specific amount of simulations, finding/expanding a leaf node for every simulation
    for i in range(Config.num_simulations):
        node = root
        temp_game = copy.deepcopy(game)
        search_path = [node]
        child_count, sim_count = 1, i+1
        #If the node is already expanded, we select a child node for the next move and update our search path
        while node.expanded():
            
            print('Selecting child ' + str(child_count) + ' for simulation ' + str(sim_count)
                + ' (Game ' + str(game_count) + ', Move ' + str(move_count) + ')')
            child_count+=1
            next_move, node = select_child(node)
            temp_game.execute_move(next_move)
            search_path.append(node)

        #When we reach a node which has not been expanded, we evaluate and expand the node then update values for 
        #The nodes in our search path, all the way back to the root node
        value = evaluate(network, temp_game, node)
        backpropagate(search_path, value, temp_game.color_to_move)

    return select_next_move(game, root), root


def evaluate(network, game, node):
    #Predicting move probabilities and game outcome using current network model
    policy_output, value = network.predict(game.encode_input())
    node.color_to_move = game.color_to_move

    #Setting our policy dictionary with the key being a legal move and the value being the probability prediction from the network
    policy = {move: math.exp(policy_output[move]) for move in game.get_legal_indexes()}
    policy_sum = sum(policy.values())
    #Normalizing policy probabilities and initializing child nodes for our parent node being evaluated
    for move, p in policy.items():
        node.children[move] = Node(p / policy_sum)

    return value


def select_child(node):
    max, res = None, ()
    #Loops over the node.children dictionary kay/value pairs returning the key(move) and value(child node) with highest UCB score
    for move, child in node.children.items():
        score = ucb_score(node, child)
        if max == None or score > max:
            res, max = (move, child), score
    return res


def select_next_move(game, root):
    print('  Selecting Move')
    visit_counts = [(child.visit_count, move) for move, child in root.children.items()]
    child_visit_count, next_move = max(visit_counts)
    return next_move


# The score for a node is based on its value, plus an exploration bonus based on the prior
def ucb_score(parent, child):
    pb_c = math.log((parent.visit_count + Config.pb_c_base + 1) /
                  Config.pb_c_base) + Config.pb_c_init
    pb_c *= math.sqrt(parent.visit_count) / (child.visit_count + 1)

    prior_score = pb_c * child.prior
    value_score = child.value()
    return prior_score + value_score


def backpropagate(search_path, value, color_to_move):
    for node in search_path:
        #Running back up the search tree updating the search path with the freshly found leaf node value
        #Adding value for same color_to_move nodes, adding 1 - value for opponent move nodes
        if node.color_to_move == color_to_move:
            node.value_sum += value
        else: node.value_sum += (1 - value)
        #Updating the node visit count
        node.visit_count += 1


def add_exploration_noise(node):
  moves = node.children.keys()
  noise = numpy.random.gamma(Config.root_dirichlet_alpha, 1, len(moves))
  frac = Config.root_exploration_fraction
  for move, n in zip(moves, noise):
    node.children[move].prior = node.children[move].prior * (1 - frac) + n * frac



def train(network, storage):
    for i in range(Config.training_steps):
        if i % Config.checkpoint_interval == 0:
            network.save()
        batch = storage.sample_batch()
        update_weights(network, batch)
    #What is the point of saving the networks? Potential fallback?
    #storage.save_network(Config.training_steps, network)


def update_weights(network, batch):
    loss = 0
    optimizer = tf.keras.optimizers.SGD(Config.learning_rate, Config.momentum, nesterov=False, name='SGD')
    for image, (target_value, target_policy) in batch:
        policy_output, value = network.predict(image)
        loss += (
            tf.losses.mean_squared_error(value, target_value) +
            tf.nn.softmax_cross_entropy_with_logits(
                logits=policy_output, labels=target_policy))

    for weights in network.get_weights():
        loss += Config.weight_decay * tf.nn.l2_loss(weights)

    optimizer.minimize(loss)




#storage = Storage()
network = Network()

for i in range(1,1000):
    info = []
    game = simulate_game(network, i)
    info = [game.encoding_history, game.node_visits, game.status]
    #storage.save_game(game)
    f = open('saved_games.txt', 'a')
    f.write(str(info))
    f.write('/')
    f.close()






        