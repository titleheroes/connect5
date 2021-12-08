import numpy as np
import random
import pygame
import math

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

AI1 = 0
AI2 = 1

EMPTY = 0
AI1_PIECE = 1
AI2_PIECE = 2

WINDOW_LENGTH = 4

def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def evaluate_window(window, piece):
	score = 0
	opp_piece = AI1_PIECE
	if piece == AI1_PIECE:
		opp_piece = AI2_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	## Score center column
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	## Score Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(board):
	return winning_move(board, AI1_PIECE) or winning_move(board, AI2_PIECE) or len(get_valid_locations(board)) == 0

def AI1_Expectimax(board, depth, alpha, beta, maximizingPlayer):
		valid_locations = get_valid_locations(board)
		is_terminal = is_terminal_node(board)
		if depth == 0 or is_terminal:
			if is_terminal:
				if winning_move(board, AI1_PIECE):
					return (None, 100000000000000)
				elif winning_move(board, AI2_PIECE):
					return (None, -10000000000000)
				else: # Game is over, no more valid moves
					return (None, 0)
			else: # Depth is zero
				return (None, score_position(board, AI1_PIECE))
		if maximizingPlayer:
			value = -math.inf
			column = random.choice(valid_locations)
			for col in valid_locations:
				row = get_next_open_row(board, col)
				b_copy = board.copy()
				drop_piece(b_copy, row, col, AI1_PIECE)
				new_score = AI1_Expectimax(b_copy, depth-1, alpha, beta, False)[1]
				if new_score > value:
					value = new_score
					column = col
				alpha = max(alpha, value)
				if alpha >= beta:
					break
			return column, value
		else: # Expecting
			value = 0
			column = random.choice(valid_locations)
			for col in valid_locations:
				row = get_next_open_row(board, col)
				b_copy = board.copy()
				drop_piece(b_copy, row, col, AI2_PIECE)
				new_score = AI1_Expectimax(b_copy, depth-1, alpha, beta, True)[1]
				if new_score <= value:
					value = new_score
					column = col
				beta = math.floor(value/len(valid_locations))
				if alpha >= beta:
					break
			return column, value

def AI2_Minimax(board, depth, alpha, beta, maximizingAI):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, AI2_PIECE):
				return (None, 100000000000000)
			elif winning_move(board, AI1_PIECE):
				return (None, -10000000000000)
			else:
				return (None, 0)
		else:
			return (None, score_position(board, AI2_PIECE))
	if maximizingAI:
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI2_PIECE)
			new_score = AI2_Minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI1_PIECE)
			new_score = AI2_Minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == AI1_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI2_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

board = create_board()
print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(AI1, AI2)
# turn = 0
turn = 1

while not game_over:

	if turn == AI1 and not game_over:	
		col, minimax_score = AI1_Expectimax(board, 5, -math.inf, math.inf, True)
	
		if is_valid_location(board, col):
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI1_PIECE)

			if winning_move(board, AI1_PIECE):
				label = myfont.render("AI1 wins!!", 0, RED)
				screen.blit(label, (40,10))
				game_over = True

			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

	# # Ask for Player 2 Input
	if turn == AI2 and not game_over:	
		col, minimax_score = AI2_Minimax(board, 5, -math.inf, math.inf, True)

		if is_valid_location(board, col):
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI2_PIECE)

			if winning_move(board, AI2_PIECE):
				label = myfont.render("AI2 wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				game_over = True

			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

	if game_over:
		pygame.time.wait(5000)