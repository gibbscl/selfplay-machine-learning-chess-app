import pygame

#Sizes
board_size = 600
tile_size = board_size / 8

#Starting board FEN
fen_initial = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

#Colors which are often used
#green = (40, 120, 65)
green = (62, 171, 145)
tan = (240, 228, 125)
white = (0,0,0)
black = (255,255,255)

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


#Class which defines numerical values for both type of piece and color of piece
#pawn:1, bishop:2, knight:3, rook:4, queen:5, king:6, white:8, black:16
class Piece:
    pawn = 1
    bishop = 2
    knight = 3
    rook = 4
    queen = 5
    king = 6
    white = 8
    black = 16


#Class for a specific move
class Move():
    def __init__(self, piece, start_tile, end_tile):
        self.piece = piece
        self.start_tile = start_tile
        self.end_tile = end_tile


#Class for the game as a whole, keeps track of castling potential, en passant capture tile, move counts
class Game():
    def __init__(self, K, Q, k, q, color_to_move, en_passant_tile, half_move_count, full_move_count):
        self.K = K
        self.Q = Q
        self.k = k
        self.q = q
        self.color_to_move = color_to_move
        self.en_passant_tile = en_passant_tile
        self.half_move_count = half_move_count
        self.full_move_count = full_move_count


#Importing piece icons and formatting those images
def import_icons():
    wk = pygame.image.load(r'.\icons\wk.png').convert_alpha()
    wk = pygame.transform.scale(wk, (int(tile_size), int(tile_size)))
    wq = pygame.image.load(r'.\icons\wq.png').convert_alpha()
    wq = pygame.transform.scale(wq, (int(tile_size), int(tile_size)))
    wr = pygame.image.load(r'.\icons\wr.png').convert_alpha()
    wr = pygame.transform.scale(wr, (int(tile_size), int(tile_size)))
    wn = pygame.image.load(r'.\icons\wn.png').convert_alpha()
    wn = pygame.transform.scale(wn, (int(tile_size), int(tile_size)))
    wb = pygame.image.load(r'.\icons\wb.png').convert_alpha()
    wb = pygame.transform.scale(wb, (int(tile_size), int(tile_size)))
    wp = pygame.image.load(r'.\icons\wp.png').convert_alpha()
    wp = pygame.transform.scale(wp, (int(tile_size), int(tile_size)))
    bk = pygame.image.load(r'.\icons\bk.png').convert_alpha()
    bk = pygame.transform.scale(bk, (int(tile_size), int(tile_size)))
    bq = pygame.image.load(r'.\icons\bq.png').convert_alpha()
    bq = pygame.transform.scale(bq, (int(tile_size), int(tile_size)))
    br = pygame.image.load(r'.\icons\br.png').convert_alpha()
    br = pygame.transform.scale(br, (int(tile_size), int(tile_size)))
    bn = pygame.image.load(r'.\icons\bn.png').convert_alpha()
    bn = pygame.transform.scale(bn, (int(tile_size), int(tile_size)))
    bb = pygame.image.load(r'.\icons\bb.png').convert_alpha()
    bb = pygame.transform.scale(bb, (int(tile_size), int(tile_size)))
    bp = pygame.image.load(r'.\icons\bp.png').convert_alpha()
    bp = pygame.transform.scale(bp, (int(tile_size), int(tile_size)))

    icons = {9:wp,10:wb,11:wn,12:wr,13:wq,14:wk,17:bp,18:bb,19:bn,20:br,21:bq,22:bk}
    return icons


#Taking in FEN string as argument and converting to array of size 64 with piece positions
def fen_to_board(fen):
    split = fen.split()
    board, color_to_move, full_move_count, half_move_count, K, Q, k, q, en_passant_tile = [], 0, 0, 0, False, False, False, False, None
    for char in split[0]:
        if char == 'P':
            board.append(Piece.white | Piece.pawn)
        elif char == 'p':
            board.append(Piece.black | Piece.pawn)
        elif char == 'B':
            board.append(Piece.white | Piece.bishop)
        elif char == 'b':
            board.append(Piece.black | Piece.bishop)
        elif char == 'N':
            board.append(Piece.white | Piece.knight)
        elif char == 'n':
            board.append(Piece.black | Piece.knight)
        elif char == 'R':
            board.append(Piece.white | Piece.rook)
        elif char == 'r':
            board.append(Piece.black | Piece.rook)
        elif char == 'Q':
            board.append(Piece.white | Piece.queen)
        elif char == 'q':
            board.append(Piece.black | Piece.queen)
        elif char == 'K':
            board.append(Piece.white | Piece.king)
        elif char == 'k':
            board.append(Piece.black | Piece.king)
        elif char.isdigit():
            empty_squares = int(char)
            for i in range(empty_squares):
                board.append(None)
    if split[1] == 'w':
        color_to_move = Piece.white
    else:
        color_to_move = Piece.black
    if 'K' in split[2]: K = True
    if 'Q' in split[2]: Q = True
    if 'k' in split[2]: k = True
    if 'q' in split[2]: q = True
    if split[3] != '-':
        en_passant_tile = chess_square_to_tile(split[3])
    half_move_count = float(split[4])
    if int(split[5]) == 1: full_move_count = 0
    else: full_move_count = int(split[5])
    game = Game(K,Q,k,q,color_to_move, en_passant_tile, half_move_count, full_move_count)

    return board, game


#Takes in chess square (ie e3) and returns tile number 
def chess_square_to_tile(square):
    letter_val = 0
    letter = square[0]
    number = int(square[1])
    if letter == 'a': letter_val = 0
    if letter == 'b': letter_val = 1
    if letter == 'c': letter_val = 2
    if letter == 'd': letter_val = 3
    if letter == 'e': letter_val = 4
    if letter == 'f': letter_val = 5
    if letter == 'g': letter_val = 6
    if letter == 'h': letter_val = 7

    tile = ((8 - number) * 8) + letter_val
    return tile


#Takes index from the board array and returns top left coordinate location on board surface
def get_coordinates(index):
    x = (index % 8) * tile_size
    y = (index // 8) * tile_size
    return (x,y)


#Returns color of specific tile (black/white) given a specific tile
def get_tile_color(tile):
    if (tile // 8 % 2 == 0 and tile % 2 == 0) or (tile // 8 % 2 != 0 and tile % 2 != 0):
            color = tan
    else:
        color = green
    return color


#Updates board gui based on board array
def update_board(board, board_surface, icons):
    for tile in range (len(board)):
        x,y = get_coordinates(tile)
        board_surface.fill(get_tile_color(tile), (x, y, tile_size, tile_size))
        if board[tile] != None:
            if (tile in range(0,8) or tile in range(56,64)) and board[tile] - get_piece_color(board[tile]) == 1:
                if get_piece_color(board[tile]) == 8:
                    board[tile] = Piece.white|Piece.queen
                else:
                    board[tile] = Piece.black|Piece.queen
            board_surface.blit(icons[board[tile]], (x, y, tile_size, tile_size))


#Returning specific tile under the mouse calculated from mouse coordinates
def get_tile_under_mouse():
    x,y = pygame.mouse.get_pos()
    tile = (x // tile_size) + ((y // tile_size)) * 8
    return int(tile)


#Drawing green box around tile which mouse is hovering
def draw_selector(screen):
    tile = get_tile_under_mouse()
    x,y = get_coordinates(tile)
    rect = (x, y, tile_size, tile_size)
    pygame.draw.rect(screen, (0, 255, 0, 50), rect, 2)


#Retrieving new tile under the mouse given that a piece has been selected already
def get_new_tile(selected_piece):
    if selected_piece:
        tile = get_tile_under_mouse()
        if tile != None:
            return tile
        else:
            return None

#Drawing icon for selected piece on top of user mouse position (dragging the piece)
def draw_drag(mouse_button_down, selected_piece, icons, board_surface):
    if mouse_button_down == True and selected_piece != None:
        x,y = pygame.mouse.get_pos()
        board_surface.blit(icons[selected_piece[0]], (x - (tile_size/2), y- (tile_size/2), tile_size, tile_size))


#Return color to move given the full move count
def get_color_to_move(move_count):
    if move_count % 2 == 0:
        color_to_move = Piece.white
    else:
        color_to_move = Piece.black
    return color_to_move

#Return color of piece
def get_piece_color(piece):
    if piece < 16:
        piece_color = Piece.white
    else:
        piece_color = Piece.black
    return piece_color


#Computing all possible moves on board, computes illegal moves as well that check is done after this computation
def compute_moves(board, color_to_move, game):
    moves = []
    offsets = [-8, -7, 1, 9, 8, 7, -1, -9]
    en_passant_move, castle_move = None, None
    for tile in range(64):
        knight_offsets = []
        king_offsets = [-8,8]
        if board[tile] != None:
            if get_piece_color(board[tile]) == color_to_move:
                piece_val = board[tile] - color_to_move
                #Taking care of sliding moves (rook, bishop, queen)
                for i in range(8):
                    if (piece_val == Piece.bishop and i % 2 != 0) or (piece_val == Piece.rook and i % 2 == 0) or piece_val == Piece.queen:
                        for j in range(tiles_to_edge[tile][i]):
                            target_tile = tile + offsets[i] * (j + 1)
                            target_tile_piece = board[target_tile]
                            if target_tile_piece != None and get_piece_color(target_tile_piece) == color_to_move:
                                break
                            found_move = Move(board[tile], tile, target_tile)
                            moves.append(found_move)
                            if target_tile_piece != None and get_piece_color(target_tile_piece) != color_to_move:
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
                            target_tile_piece = board[target_tile]
                            if target_tile_piece != None and get_piece_color(target_tile_piece) == color_to_move:
                                continue
                            found_move = Move(board[tile], tile, target_tile)
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
                            target_tile_piece = board[target_tile]
                            if target_tile_piece != None and get_piece_color(target_tile_piece) == color_to_move:
                                continue
                            found_move = Move(board[tile], tile, target_tile)
                            moves.append(found_move)
                #taking care of pawn moves excluding en passant moves
                if piece_val == Piece.pawn:
                    if color_to_move == 8:
                        change, right, left = -8, -7, -9
                        if tiles_to_edge[tile][6] >= 1 and tile+left >=0 and tile+left <= 63:
                            if board[tile+left] != None and get_piece_color(board[tile+left]) != color_to_move:
                                found_move = Move(board[tile], tile, tile+left)
                                moves.append(found_move)
                        if tiles_to_edge[tile][2] >= 1 and tile+right >=0 and tile+right <= 63:
                            if board[tile+right] != None and get_piece_color(board[tile+right]) != color_to_move:
                                found_move = Move(board[tile], tile, tile+right)
                                moves.append(found_move)
                        if tile // 8 == 6 and board[tile - 16] == None:
                            temp = 2
                        else:
                            temp = 1
                    else:
                        change, right, left = 8, 7, 9
                        if tiles_to_edge[tile][2] >= 1 and tile+left >=0 and tile+left <= 63:
                            if board[tile+left] != None and get_piece_color(board[tile+left]) != color_to_move:
                                found_move = Move(board[tile], tile, tile+left)
                                moves.append(found_move)
                        if tiles_to_edge[tile][6] >= 1 and tile+right >=0 and tile+right <= 63:
                            if board[tile+right] != None and get_piece_color(board[tile+right]) != color_to_move:
                                found_move = Move(board[tile], tile, tile+right)
                                moves.append(found_move)
                        if tile // 8 == 1 and board[tile + 16] == None:
                            temp = 2
                        else:
                            temp = 1
                    for i in range(temp):
                        target_tile = tile + (change * (i + 1))
                        if target_tile >= 0 and target_tile <= 63:
                            target_tile_piece = board[target_tile]
                            if target_tile_piece != None:
                                continue
                            found_move = Move(board[tile], tile, target_tile)
                            moves.append(found_move)
    #Taking care of en passant moves
    if game.en_passant_tile != None:
        if color_to_move == Piece.white:
            if board[game.en_passant_tile + 7] == Piece.white|Piece.pawn:
                en_passant_move = Move(board[game.en_passant_tile + 7], game.en_passant_tile + 7, game.en_passant_tile)
                moves.append(en_passant_move)
            if board[game.en_passant_tile + 9] == Piece.white|Piece.pawn:
                en_passant_move = Move(board[game.en_passant_tile + 9], game.en_passant_tile + 9, game.en_passant_tile)
                moves.append(en_passant_move)
        elif color_to_move == Piece.black:
            if board[game.en_passant_tile - 7] == Piece.black|Piece.pawn:
                en_passant_move = Move(board[game.en_passant_tile - 7], game.en_passant_tile - 7, game.en_passant_tile)
                moves.append(en_passant_move)
            if board[game.en_passant_tile - 9] == Piece.black|Piece.pawn:
                en_passant_move = Move(board[game.en_passant_tile - 9], game.en_passant_tile - 9, game.en_passant_tile)
                moves.append(en_passant_move)
    #Taking care of castling moves
    if game.K == True and board[61] == None and board[62] == None \
        and is_legal_move(Piece.white|Piece.king, 60, 61, board, game):
        castle_move = Move(Piece.king|Piece.white, 60, 62)
        moves.append(castle_move)
    if game.Q == True and board[57] == None and board[58] == None and board[59] == None \
        and is_legal_move(Piece.white|Piece.king, 60, 59, board, game) and is_legal_move(Piece.white|Piece.king, 60, 58, board, game):
        castle_move = Move(Piece.king|Piece.white, 60, 57)
        moves.append(castle_move)
    if game.k == True and board[5] == None and board[6] == None \
        and is_legal_move(Piece.black|Piece.king, 4, 5, board, game):
        castle_move = Move(Piece.king|Piece.black, 4, 6)
        moves.append(castle_move)
    if game.q == True and board[1] == None and board[2] == None and board[3] == None \
        and is_legal_move(Piece.black|Piece.king, 4, 3, board, game) and is_legal_move(Piece.white|Piece.king, 4, 2, board, game):
        castle_move = Move(Piece.king|Piece.black, 4, 1)
        moves.append(castle_move)
    return moves


#Drawing possible moves for the piece selected
def draw_moves(possible_moves, selected_piece, board, game, screen):
    if selected_piece != None:
        for move in possible_moves:
            if move.piece == selected_piece[0] and move.start_tile == selected_piece[1]:
                tile = move.end_tile
                x,y = get_coordinates(tile)
                rect = (x, y, tile_size, tile_size)
                pygame.draw.rect(screen, (255, 0, 0, 50), rect, 2)


#Checking if attempted move is legal (ie does not put player in check)
def is_legal_move(piece, start_tile, end_tile, board, game):
    flag = False
    color = get_piece_color(piece)
    temp_board = board.copy()
    temp_board[start_tile] = None
    temp_board[end_tile] = piece
    if not is_in_check(temp_board, color, game): flag = True
    return flag


#Checking if a given player is in check
def is_in_check(board, color, game):
    in_check = False
    opponent_moves = compute_moves(board, 24^color, game)
    for move in opponent_moves:
        if board[move.end_tile] == color|Piece.king:
            in_check = True
    return in_check


#Taking all possible moves and returning moves which are not legal (ie moves putting yourself in check, etc.)
def prune_possible_moves(possible_moves, board, game):
    all_legal_moves = []
    for move in possible_moves:
        if is_legal_move(move.piece, move.start_tile, move.end_tile, board, game):
            all_legal_moves.append(move)
    return all_legal_moves

#Check if move is in set of all legal moves
def move_is_legal(legal_moves, move):
    flag = False
    for legal_move in legal_moves:
        if legal_move.piece == move.piece and legal_move.start_tile == move.start_tile and legal_move.end_tile == move.end_tile:
            flag = True
    return flag



def main(gui):
    #Preparing pygame module for use, initializing variables and data structures used
    pygame.init()
    clock = pygame.time.Clock()
    all_moves, prev_move, winner, draw = [], None, None, None
    

    if(gui):
        screen = pygame.display.set_mode((board_size, board_size))
        icons = import_icons()
        board_surface = pygame.Surface((board_size, board_size))

    board, game = fen_to_board(fen_initial)
    selected_piece, new_tile, mouse_button_down = None, None, False
    possible_moves = compute_moves(board, get_color_to_move(game.full_move_count), game)
    legal_moves = prune_possible_moves(possible_moves, board, game)

    while True:
        color_to_move = get_color_to_move(game.full_move_count)
        tile = get_tile_under_mouse()
        piece = board[tile]
        events = pygame.event.get()   
        for e in events:
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN and mouse_button_down == False:
                if piece != None and color_to_move == get_piece_color(piece):
                    mouse_button_down = True
                    selected_piece = piece, tile
                    old_tile = tile
                    board[tile] = None
            if e.type == pygame.MOUSEBUTTONUP and mouse_button_down == True:
                mouse_button_down = False
                piece, old_tile = selected_piece
                temp = board[new_tile]
                move = Move(piece, old_tile, new_tile)
                #Checking to make sure you are actually moving and piece and making a legal move
                if new_tile != None and new_tile != old_tile and move_is_legal(legal_moves, move):

                    #Taking care of en passant moves
                    if (piece - color_to_move == 1) and (abs(new_tile - old_tile) ==  9 \
                        or abs(new_tile - old_tile) ==  7) and board[new_tile] == None:
                        board[new_tile] = piece
                        if color_to_move == 16:
                            board[new_tile - 8] = None
                        else:
                            board[new_tile + 8] = None
                    #Taking care of castle moves
                    elif piece == Piece.white|Piece.king and old_tile == 60 and new_tile == 62:
                        board[62] = Piece.white|Piece.king
                        board[61] = Piece.white|Piece.rook
                        board[63] = None
                    elif piece == Piece.white|Piece.king and old_tile == 60 and new_tile == 57:
                        board[57] = Piece.white|Piece.king
                        board[58] = Piece.white|Piece.rook
                        board[56] = None
                    elif piece == Piece.black|Piece.king and old_tile == 4 and new_tile == 1:
                        board[1] = Piece.black|Piece.king
                        board[2] = Piece.black|Piece.rook
                        board[0] = None
                    elif piece == Piece.black|Piece.king and old_tile == 4 and new_tile == 6:
                        board[6] = Piece.black|Piece.king
                        board[5] = Piece.black|Piece.rook
                        board[7] = None
                    #Taking care of all other moves
                    else:
                        board[new_tile] = piece
                        board[old_tile] = None

                    if (temp == None) and (piece  - color_to_move != Piece.pawn):
                        game.half_move_count += 0.5
                    else:
                        game.half_move_count = 0
                    #Updating move count and adding most recent move to the running list of all moves
                    game.full_move_count+=1
                    recent_move = Move(piece, old_tile, new_tile)
                    all_moves.append(recent_move)
                    prev_move = recent_move

                    #Updating en passant tile
                    if prev_move != None and (prev_move.piece - color_to_move == Piece.pawn) and (abs(new_tile - old_tile) == 16):
                        if color_to_move == Piece.white: game.en_passant_tile = new_tile + 8
                        else: game.en_passant_tile = new_tile - 8    
                    else:
                        game.en_passant_tile = None

                    #Updating flags for potential castles
                    if board[60] != Piece.white|Piece.king: game.K, game.Q = False, False
                    if board[63] != Piece.white|Piece.rook: game.K = False
                    if board[56] != Piece.white|Piece.rook: game.Q = False
                    if board[4] != Piece.black|Piece.king: game.k, game.q = False, False
                    if board[7] != Piece.black|Piece.rook: game.k = False
                    if board[0] != Piece.black|Piece.rook: game.q = False

                    #Recomputing possible moves after most recent movement
                    possible_moves = compute_moves(board, get_color_to_move(game.full_move_count), game)
                    legal_moves = prune_possible_moves(possible_moves, board, game)

                    #Checking win/draw conditions
                    if legal_moves == []:
                        winner = 24^get_color_to_move(game.full_move_count)
                    elif game.half_move_count == 50:
                        draw = 1

                #If a valid move isn't made or if a piece is picked up and put down at same spot, don't do anything
                else:
                    board[old_tile] = selected_piece[0]
                    if new_tile != old_tile: board[new_tile] = temp
                selected_piece = None

        
        new_tile = get_new_tile(selected_piece)
        print(board)

        if(gui):
            update_board(board, board_surface, icons)
            draw_drag(mouse_button_down, selected_piece, icons, board_surface)
            screen.blit(board_surface,(0,0))
            draw_selector(screen)
            draw_moves(legal_moves, selected_piece, board, game, screen)

        #Ending game if win/draw conditions are met
        if winner != None:
            if winner == 8: win_color = 'White'
            else: win_color = 'Black'
            print("Winner is: " + win_color)
            break
        elif draw != None:
            print("Game ended in a draw")
            break
        
        
        
        clock.tick(60)
        if(gui):
            pygame.display.flip()

    #Quits once window is closed
    pygame.quit()

#gui = True
#main(gui)