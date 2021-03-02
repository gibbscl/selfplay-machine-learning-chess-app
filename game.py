import copy, collections

#Starting board FEN
fen_initial = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


#Precomputing the tiles to the edge of the board for each tile on the board
tiles_to_edge = []
for tile in range(64):
    direction_index = []
    num_north = tile // 8
    num_south = 7 - num_north
    num_west = tile - ((tile // 8) * 8)
    num_east = 7 - num_west
    direction_index.append(num_north)
    direction_index.append(min(num_north, num_east))
    direction_index.append(num_east)
    direction_index.append(min(num_south, num_east))
    direction_index.append(num_south)
    direction_index.append(min(num_south, num_west))
    direction_index.append(num_west)
    direction_index.append(min(num_north, num_west))
    tiles_to_edge.append(direction_index)

N,NE,E,SE,S,SW,W,NW = -8, -7, 1, 9, 8, 7, -1, -9
#Tile offsets for knights and directional moves, respectively
knight_offsets = [-17, -15, -10, -6, 6, 10, 15, 17]
#N->NE->E->SE->S->SW->W->NW
direction_offsets = [N,NE,E,SE,S,SW,W,NW]
dir_dict= {N:0, NE:1, E:2, SE:3, S:4, SW:5, W:6, NW:7}
knight_dict = {-17:0, -15:1, -10:2, -6:3, 6:4, 10:5, 15:6, 17:7}


#Class which defines numerical values for both type of piece and color of piece
#pawn:1, bishop:2, knight:3, rook:4, queen:5, king:6, white:8, black:16
class Piece():
    pawn = 1
    bishop = 2
    knight = 3
    rook = 4
    queen = 5
    king = 6
    white = 8
    black = 16


#Class for a specific move
class Move(object):
    def __init__(self, piece, start_tile, end_tile, direction, distance, promotion = None):
        self.piece = piece
        self.start_tile = start_tile
        self.end_tile = end_tile
        self.direction = direction
        self.distance = distance
        self.promotion = promotion


#Class for the game as a whole, keeps track of castling potential, en passant capture tile, move counts
class Game(object):
    def __init__(self, fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' ):
        self.load_fen(fen)
        self.history = [None, None, None, None, None, None, None]
        self.node_visits = []
        self.encoding_history = [self.encode_input()]
        self.all_moves = get_all_moves()
        self.executed_moves = []
    
    #Taking in FEN string as argument and loading necessary values into game variables
    def load_fen(self,fen):
        split = fen.split()
        self.board, self.color_to_move, self.full_move_count, self.half_move_count = [], 0, 0, 0 
        self.K, self.Q, self.k, self.q, self.en_passant_tile = False, False, False, False, None
        for char in split[0]:
            if char == 'P':
                self.board.append(Piece.white | Piece.pawn)
            elif char == 'p':
                self.board.append(Piece.black | Piece.pawn)
            elif char == 'B':
                self.board.append(Piece.white | Piece.bishop)
            elif char == 'b':
                self.board.append(Piece.black | Piece.bishop)
            elif char == 'N':
                self.board.append(Piece.white | Piece.knight)
            elif char == 'n':
                self.board.append(Piece.black | Piece.knight)
            elif char == 'R':
                self.board.append(Piece.white | Piece.rook)
            elif char == 'r':
                self.board.append(Piece.black | Piece.rook)
            elif char == 'Q':
                self.board.append(Piece.white | Piece.queen)
            elif char == 'q':
                self.board.append(Piece.black | Piece.queen)
            elif char == 'K':
                self.board.append(Piece.white | Piece.king)
            elif char == 'k':
                self.board.append(Piece.black | Piece.king)
            elif char.isdigit():
                empty_squares = int(char)
                for i in range(empty_squares):
                    self.board.append(None)
        if split[1] == 'w':
            self.color_to_move = Piece.white
        else:
            self.color_to_move = Piece.black
        if 'K' in split[2]: self.K = True
        if 'Q' in split[2]: self.Q = True
        if 'k' in split[2]: self.k = True
        if 'q' in split[2]: self.q = True
        if split[3] != '-':
            self.en_passant_tile = chess_square_to_tile(split[3])
        self.half_move_count = float(split[4])
        if int(split[5]) == 1: self.full_move_count = 0
        else: self.full_move_count = int(split[5])

        #Checking game status
        possible_moves = self.compute_moves()
        legal_moves = self.prune_possible_moves(possible_moves)

        #Checking win/draw conditions
        if legal_moves == [] and self.is_in_check(self.color_to_move):
            if self.color_to_move == Piece.black: self.status = 1
            else: self.status = -1
        elif (legal_moves == [] and not self.is_in_check(self.color_to_move)) or self.half_move_count >= 50: self.status = 0
        else: self.status = None
        return self
    
    #Return color of piece
    def get_piece_color(self, piece):
        if piece < 16:
            piece_color = Piece.white
        else:
            piece_color = Piece.black
        return piece_color

    #Checking if attempted move is legal (ie does not put player in check)
    def is_legal_move(self, piece, start_tile, end_tile):
        flag = False
        color = self.get_piece_color(piece)
        temp_game = copy.deepcopy(self)
        temp_game.board[start_tile] = None
        temp_game.board[end_tile] = piece
        if not temp_game.is_in_check(color): flag = True
        return flag

    #Checking if a given player is in check
    def is_in_check(self, color):
        in_check = False
        self.full_move_count+=1
        self.color_to_move = self.color_to_move^24
        opponent_moves = self.compute_moves()
        for move in opponent_moves:
            if self.board[move.end_tile] == color|Piece.king:
                in_check = True
        return in_check
    
    #Taking all possible moves and returning moves which are not legal (ie moves putting yourself in check, etc.)
    def prune_possible_moves(self, possible_moves):
        all_legal_moves = []
        for move in possible_moves:
            if self.is_legal_move(move.piece, move.start_tile, move.end_tile):
                all_legal_moves.append(move)
        return all_legal_moves

    #Check if move is in set of all legal moves
    def move_is_legal(self, legal_moves, move):
        flag = False
        for legal_move in legal_moves:
            if legal_move.piece == move.piece and legal_move.start_tile == move.start_tile and legal_move.end_tile == move.end_tile:
                flag = True
        return flag
    
    #Computing all possible moves on board, computes illegal moves as well that check is done after this computation
    def compute_moves(self):
        moves = []
        offsets = [-8, -7, 1, 9, 8, 7, -1, -9]
        en_passant_move, castle_move = None, None
        for tile in range(64):
            knight_offsets = []
            king_offsets = [-8,8]
            if self.board[tile] != None:
                if self.get_piece_color(self.board[tile]) == self.color_to_move:
                    piece_val = self.board[tile] - self.color_to_move
                    #Taking care of sliding moves (rook, bishop, queen)
                    for i in range(8):
                        if (piece_val == Piece.bishop and i % 2 != 0) or (piece_val == Piece.rook and i % 2 == 0) or piece_val == Piece.queen:
                            for j in range(tiles_to_edge[tile][i]):
                                target_tile = tile + offsets[i] * (j + 1)
                                target_tile_piece = self.board[target_tile]
                                if target_tile_piece != None and self.get_piece_color(target_tile_piece) == self.color_to_move:
                                    break
                                found_move = Move(self.board[tile], tile, target_tile, i, j+1)
                                moves.append(found_move)
                                if target_tile_piece != None and self.get_piece_color(target_tile_piece) != self.color_to_move:
                                    break
                    #Taking care of knight moves
                    if piece_val == Piece.knight:
                        if tiles_to_edge[tile][2] >= 1: 
                            knight_offsets.append(-15)
                            knight_offsets.append(17)
                        if tiles_to_edge[tile][2] >= 2: 
                            knight_offsets.append(10)
                            knight_offsets.append(-6)
                        if tiles_to_edge[tile][6] >= 1: 
                            knight_offsets.append(15)
                            knight_offsets.append(-17)
                        if tiles_to_edge[tile][6] >= 2: 
                            knight_offsets.append(-10)
                            knight_offsets.append(6)
                        for offset in knight_offsets:
                            target_tile = tile + offset
                            if target_tile >= 0 and target_tile <= 63:
                                target_tile_piece = self.board[target_tile]
                                if target_tile_piece != None and self.get_piece_color(target_tile_piece) == self.color_to_move:
                                    continue
                                found_move = Move(self.board[tile], tile, target_tile, knight_dict[offset], 1)
                                moves.append(found_move)
                    #Taking care of king moves excluding castling
                    if piece_val == Piece.king:
                        if tiles_to_edge[tile][2] >= 1: 
                            king_offsets.append(-7)
                            king_offsets.append(1)
                            king_offsets.append(9)
                        if tiles_to_edge[tile][6] >= 1: 
                            king_offsets.append(7)
                            king_offsets.append(-1)
                            king_offsets.append(-9)
                        for offset in king_offsets:
                            target_tile = tile + offset
                            if target_tile >= 0 and target_tile <= 63:
                                target_tile_piece = self.board[target_tile]
                                if target_tile_piece != None and self.get_piece_color(target_tile_piece) == self.color_to_move:
                                    continue
                                found_move = Move(self.board[tile], tile, target_tile, dir_dict[offset], 1)
                                moves.append(found_move)
                    #taking care of pawn moves excluding en passant moves
                    if piece_val == Piece.pawn:
                        pawn_moves = []
                        if self.color_to_move == 8:
                            change, right, left = -8, -7, -9
                            if tiles_to_edge[tile][6] >= 1 and tile+left >=0 and tile+left <= 63:
                                if self.board[tile+left] != None and self.get_piece_color(self.board[tile+left]) != self.color_to_move:
                                    found_move = Move(self.board[tile], tile, tile+left, dir_dict[left], 1)
                                    pawn_moves.append(found_move)
                            if tiles_to_edge[tile][2] >= 1 and tile+right >=0 and tile+right <= 63:
                                if self.board[tile+right] != None and self.get_piece_color(self.board[tile+right]) != self.color_to_move:
                                    found_move = Move(self.board[tile], tile, tile+right, dir_dict[right], 1)
                                    pawn_moves.append(found_move)
                            if tile // 8 == 6 and self.board[tile - 16] == None:
                                temp = 2
                            else:
                                temp = 1
                        else:
                            change, right, left = 8, 7, 9
                            if tiles_to_edge[tile][2] >= 1 and tile+left >=0 and tile+left <= 63:
                                if self.board[tile+left] != None and self.get_piece_color(self.board[tile+left]) != self.color_to_move:
                                    found_move = Move(self.board[tile], tile, tile+left, dir_dict[left], 1)
                                    pawn_moves.append(found_move)
                            if tiles_to_edge[tile][6] >= 1 and tile+right >=0 and tile+right <= 63:
                                if self.board[tile+right] != None and self.get_piece_color(self.board[tile+right]) != self.color_to_move:
                                    found_move = Move(self.board[tile], tile, tile+right, dir_dict[right], 1)
                                    pawn_moves.append(found_move)
                            if tile // 8 == 1 and self.board[tile + 16] == None:
                                temp = 2
                            else:
                                temp = 1
                        for i in range(temp):
                            target_tile = tile + (change * (i + 1))
                            if target_tile >= 0 and target_tile <= 63:
                                target_tile_piece = self.board[target_tile]
                                if target_tile_piece != None:
                                    continue
                                found_move = Move(self.board[tile], tile, target_tile, dir_dict[change], i+1)
                                pawn_moves.append(found_move)
                        #Checking if pawn move is to last rank, if so add one move for knight promotion and one for queen promotion
                        for pawn_move in pawn_moves:
                            if (pawn_move.end_tile >=0 and pawn_move.end_tile<=7) or (pawn_move.end_tile >=56 and pawn_move.end_tile<=63):
                                knight_promotion = Move(pawn_move.piece, pawn_move.start_tile, pawn_move.end_tile, pawn_move.direction, 1, 1)
                                queen_promotion = Move(pawn_move.piece, pawn_move.start_tile, pawn_move.end_tile, pawn_move.direction, 1, 2)
                                moves.append(knight_promotion)
                                moves.append(queen_promotion)
                            else: moves.append(pawn_move)
        #Taking care of en passant moves
        if self.en_passant_tile != None:
            if self.color_to_move == Piece.white:
                if self.board[self.en_passant_tile + 7] == Piece.white|Piece.pawn:
                    en_passant_move = Move(self.board[self.en_passant_tile + 7], self.en_passant_tile + 7, self.en_passant_tile, dir_dict[7], 1)
                    moves.append(en_passant_move)
                if self.board[self.en_passant_tile + 9] == Piece.white|Piece.pawn:
                    en_passant_move = Move(self.board[self.en_passant_tile + 9], self.en_passant_tile + 9, self.en_passant_tile, dir_dict[9], 1)
                    moves.append(en_passant_move)
            elif self.color_to_move == Piece.black:
                if self.board[self.en_passant_tile - 7] == Piece.black|Piece.pawn:
                    en_passant_move = Move(self.board[self.en_passant_tile - 7], self.en_passant_tile - 7, self.en_passant_tile, dir_dict[-7], 1)
                    moves.append(en_passant_move)
                if self.board[self.en_passant_tile - 9] == Piece.black|Piece.pawn:
                    en_passant_move = Move(self.board[self.en_passant_tile - 9], self.en_passant_tile - 9, self.en_passant_tile, dir_dict[-9], 1)
                    moves.append(en_passant_move)
        #Taking care of castling moves
        if self.K == True and self.board[61] == None and self.board[62] == None \
            and self.is_legal_move(Piece.white|Piece.king, 60, 61):
            castle_move = Move(Piece.king|Piece.white, 60, 62, 2, 2)
            moves.append(castle_move)
        if self.Q == True and self.board[57] == None and self.board[58] == None and self.board[59] == None \
            and self.is_legal_move(Piece.white|Piece.king, 60, 59) and self.is_legal_move(Piece.white|Piece.king, 60, 58):
            castle_move = Move(Piece.king|Piece.white, 60, 57, 6, 3)
            moves.append(castle_move)
        if self.k == True and self.board[5] == None and self.board[6] == None \
            and self.is_legal_move(Piece.black|Piece.king, 4, 5):
            castle_move = Move(Piece.king|Piece.black, 4, 6, 6, 2)
            moves.append(castle_move)
        if self.q == True and self.board[1] == None and self.board[2] == None and self.board[3] == None \
            and self.is_legal_move(Piece.black|Piece.king, 4, 3) and self.is_legal_move(Piece.white|Piece.king, 4, 2):
            castle_move = Move(Piece.king|Piece.black, 4, 1, 2, 3)
            moves.append(castle_move)
        return moves
    
    #Getting list of all legal moves for current game
    def get_legal_moves(self):
        possible_moves = self.compute_moves()
        legal_moves = self.prune_possible_moves(possible_moves)
        return legal_moves
    
    #Executing a specific move
    def execute_move(self, move):
        #Updating game history
        self.history.pop()
        self.history.insert(0,self.board)
        #Checking if move is 3-tuple or move class object
        if isinstance(move, int):
            move = self.convert_move(move)
        #Taking care of en passant moves
        if (move.piece - self.color_to_move == 1) and (abs(move.end_tile - move.start_tile) ==  9 \
        or abs(move.end_tile - move.start_tile) ==  7) and self.board[move.end_tile] == None:
            self.board[move.end_tile] = piece
            if self.color_to_move == 16:
                self.board[move.end_tile - 8] = None
            else:
                self.board[move.end_tile + 8] = None
        #Taking care of castle moves
        elif move.piece == Piece.white|Piece.king and move.start_tile == 60 and move.end_tile == 62:
            self.board[62] = Piece.white|Piece.king
            self.board[61] = Piece.white|Piece.rook
            self.board[63] = None
        elif move.piece == Piece.white|Piece.king and move.start_tile == 60 and move.end_tile == 57:
            self.board[57] = Piece.white|Piece.king
            self.board[58] = Piece.white|Piece.rook
            self.board[56] = None
        elif move.piece == Piece.black|Piece.king and move.start_tile == 4 and move.end_tile == 1:
            self.board[1] = Piece.black|Piece.king
            self.board[2] = Piece.black|Piece.rook
            self.board[0] = None
        elif move.piece == Piece.black|Piece.king and move.start_tile == 4 and move.end_tile == 6:
            self.board[6] = Piece.black|Piece.king
            self.board[5] = Piece.black|Piece.rook
            self.board[7] = None
        #Taking care of pawn promotion moves
        elif move.promotion != None:
            if move.promotion == 2: promotion_type = Piece.queen
            else: prmotion_type = Piece.knight
            self.board[move.end_tile] = self.color_to_move|promotion_type
            self.board[move.start_tile] = None
        #Taking care of all other moves
        else:
            self.board[move.end_tile] = move.piece
            self.board[move.start_tile] = None


        #Updating half move count
        if (move.piece  - self.color_to_move != Piece.pawn):
            self.half_move_count += 0.5
        else:
            self.half_move_count = 0
        #Updating move count and adding most recent move to the running list of all moves
        self.full_move_count+=1
        
        #Updating en passant tile
        if (move.piece - self.color_to_move == Piece.pawn) and (abs(move.end_tile - move.start_tile) == 16):
            if self.color_to_move == Piece.white: self.en_passant_tile = move.end_tile + 8
            else: self.en_passant_tile = move.end_tile - 8    
        else:
            self.en_passant_tile = None
        
        #Updating flags for potential castles
        if self.board[60] != Piece.white|Piece.king: self.K, self.Q = False, False
        if self.board[63] != Piece.white|Piece.rook: self.K = False
        if self.board[56] != Piece.white|Piece.rook: self.Q = False
        if self.board[4] != Piece.black|Piece.king: self.k, self.q = False, False
        if self.board[7] != Piece.black|Piece.rook: self.k = False
        if self.board[0] != Piece.black|Piece.rook: self.q = False

        #Updating color to move 
        self.color_to_move = self.color_to_move^24
        #Recalculating legal moves for opponent to check win conditions
        legal_moves = self.get_legal_moves()

        #Checking win/draw conditions
        if legal_moves == [] and self.is_in_check(self.color_to_move):
            if self.color_to_move == Piece.black: self.status = 1
            else: self.status = -1
        elif legal_moves == [] and not self.is_in_check(self.color_to_move):
            self.status = 0
        elif self.half_move_count >= 50:
            self.status = 0

        #Adding encoding after move execution to the list of encoded game states
        self.encoding_history.append(self.encode_input())
        #Adding executed move to executed moves list
        self.executed_moves.append(move)

        return legal_moves
        

    #Encoding input for Network
    def encode_input(self):
        input = []
        history = copy.deepcopy(self.history)
        history.insert(0, self.board)
        rank = []
        for i in range(8):
            file = []
            for j in range(8):
                features = []
                for board in history:
                    if board != None:
                        tile = (i * 8) + j
                        tile_enc = encode_tile(board, tile)
                        for val in tile_enc:
                            features.append(val)
                    else:
                        for x in range(12):
                            features.append(0)
                state_enc = encode_game_state(self)
                for val in state_enc:
                    features.append(val)

                file.append(features)
            rank.append(file)
        input.append(rank)
        return input

    #Obtaining the index position of legal moves from the constant list of all possible moves
    def get_legal_indexes(self):
        legal_moves = self.get_legal_moves()
        indexes = legal_indexes(self.all_moves, legal_moves)
        return indexes


    #Updating list of node visits within specific game
    def update_stats(self, root):
        sum_visits = sum(child.visit_count for child in root.children.values())
        self.node_visits.append([
            root.children[move_index].visit_count / sum_visits if move_index in root.children else 0
            for move_index in range(4864)
    ])


    #Converting (start_tile, end_tile, promotion) action into Move object
    def convert_move(self, move_index):
        move = self.all_moves[move_index]
        start_tile, end_tile, dir, dis, promotion = move
        piece = self.color_to_move|self.board[start_tile]
        Move(piece, start_tile, end_tile, dir, dis, promotion)
        #offset = end_tile - start_tile
        #if offset in knight_offsets:
        #    dir, dis = knight_dict[offset], 1
        #else:
        #    dir = dir_dict[offset]
        #    dis = offset / dir
        converted_move = Move(piece, start_tile, end_tile, dir, dis, promotion)
        return converted_move

    def make_image(self, move_number):
        return self.encoding_history[move_number]

    def make_target(self, move_number):
        if self.status == None: status = 1
        else: status = self.status
        return self.node_visits[move_number], float(status)


#Hot encoding features specific to a tile on a given board
def encode_tile(board, tile):
    white_pawn, white_rook, white_knight, white_bishop, white_queen, white_king = 0,0,0,0,0,0
    black_pawn, black_rook, black_knight, black_bishop, black_queen, black_king = 0,0,0,0,0,0
    piece = board[tile]
    if piece != None:
        if piece < 16: color = 8
        else: color = 16
        value = piece - color
        if value == Piece.pawn:
            if color == Piece.white: white_pawn = 1
            else: black_pawn = 1
        elif value == Piece.rook:
            if color == Piece.white: white_rook = 1
            else: black_rook = 1
        elif value == Piece.knight:
            if color == Piece.white: white_knight = 1
            else: black_knight = 1
        elif value == Piece.bishop:
            if color == Piece.white: white_bishop = 1
            else: black_bishop = 1
        elif value == Piece.queen:
            if color == Piece.white: white_queen = 1
            else: black_queen = 1
        elif value == Piece.king:
            if color == Piece.white: white_king = 1
            else: black_king = 1
    
    return (white_pawn, white_rook, white_knight, white_bishop, white_queen, white_king,
    black_pawn, black_rook, black_knight, black_bishop, black_queen, black_king)


#Hot encoding the current game state
def encode_game_state(game):
    white_king_castle, white_queen_castle, black_king_castle, black_queen_castle = 0,0,0,0
    full_move_count, half_move_count, color_to_move = 0,0,0
    if game.K: white_king_castle = 1
    if game.Q: white_queen_castle = 1
    if game.k: black_king_castle = 1
    if game.q: black_queen_castle = 1
    if game.color_to_move == 8:
        color_to_move = 1
    else: color_to_move = 0
    full_move_count = game.full_move_count
    half_move_count = game.half_move_count

    return (white_king_castle, white_queen_castle, black_king_castle, black_queen_castle,
    full_move_count, half_move_count, color_to_move)


#Helper function to get constant list of all possible
def get_all_moves():
    all_moves = []
    for start_tile in range(64):
        for dir in range(8):
            for dis in range(1,8):
                offset = direction_offsets[dir]
                end_tile = start_tile + (offset * dis)
                all_moves.append((start_tile, end_tile, dir, dis, None))
        for offset in knight_offsets:
            end_tile = start_tile + offset
            all_moves.append((start_tile, end_tile, knight_dict[offset], 1, None))
        for dir in (0,1,3,4,5,7):
            for promotion in (1,2):
                end_tile = start_tile + direction_offsets[dir]
                all_moves.append((start_tile, end_tile, dir, 1, promotion))
    return all_moves


#Helper function to get list of indexes for legal move position in list of all possible moves
def legal_indexes(all_moves, legal_moves):
    indexes = []
    for legal in legal_moves:
        for i in [i for i, all in enumerate(all_moves) if all == ((legal.start_tile, legal.end_tile, legal.direction,legal.distance, legal.promotion))]:
            indexes.append(i)
    return indexes







