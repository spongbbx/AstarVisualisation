import pygame
import math
from random import shuffle, randint
from queue import PriorityQueue
import random

WIDTH = 700
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A Star Visualisation")
cell_size = 1
RED = (255, 161, 161)
GREEN = (156, 255, 180)
BLUE = (0, 0, 255)
YELLOW = (255, 225, 70)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (0, 0, 255)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

lst = []

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False


def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	ROWS = 70
	grid = make_grid(ROWS, width)

	start = None
	end = None

	run = True
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]:
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)

				spot = grid[row][col]
				if not start and spot != end:
					start = spot
					start.make_start()

				elif not end and spot != start:
					end = spot
					end.make_end()

				elif spot != end and spot != start:
					spot.make_barrier()
					bar = str(spot)

			elif pygame.mouse.get_pressed()[2]:
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)

				if event.key == pygame.K_UP:
					ROWS = ROWS + 1
					print(ROWS)
					start = None
					end = None
					grid = make_grid(ROWS, width)

				if event.key == pygame.K_DOWN:
					ROWS = ROWS - 1
					print(ROWS)
					start = None
					end = None
					grid = make_grid(ROWS, width)

				if event.key == pygame.K_r:
					start = None
					end = None
					grid = make_grid(ROWS, width)

					for i in range(0,ROWS):
						for j in range(0, ROWS):
							row = i
							col = j
							lst.append(row + col)
							spot = grid[row][col]
							spot.make_barrier()

					passage_list = []
					potential_passage_list = []
					impossible_passage = []
					random_cell = []
					done = False

					def one_connection(row, col):
						count = 0

						if [row + cell_size, col] in passage_list:
							count += 1
						if [row - cell_size, col] in passage_list:
							count += 1
						if [row, col + cell_size] in passage_list:
							count += 1
						if [row, col - cell_size] in passage_list:
							count += 1

						if count <= 1:
							return True
						else:
							return False

					def valid_cell(row, col):
						if [row, col] in potential_passage_list:
							impossible_passage.append([row, col])
						elif [row, col] in impossible_passage:
							impossible_passage.append([row, col])
						elif row < 0 or row >= ROWS - cell_size or col < 0 or col >= ROWS - cell_size:
							impossible_passage.append([row, col])
						elif not one_connection(row, col):
							impossible_passage.append([row, col])
						elif (([row + cell_size, col + cell_size] in passage_list and [row + cell_size, col] not in
							   passage_list and [row, col + cell_size] not in passage_list) or
							  ([row + cell_size, col - cell_size] in passage_list and [row + cell_size, col] not in
							   passage_list and [row, col - cell_size] not in passage_list) or
							  ([row - cell_size, col + cell_size] in passage_list and [row - cell_size, col] not in
							   passage_list and [row, col + cell_size] not in passage_list) or
							  ([row - cell_size, col - cell_size] in passage_list and [row - cell_size, col] not in
							   passage_list and [row, col - cell_size] not in passage_list)):

							impossible_passage.append([row, col])
						elif [row, col] not in passage_list:
							return True

					def maze_passage(row, col):
						block_passage_list = []

						potential_passage_list.remove([row, col])
						if valid_cell(row, col):
							spot = grid[row][col]
							spot.reset()
							passage_list.append([row, col])
							lst.append(row)
							lst.append(col)

							if valid_cell(row + 1, col):
								block_passage_list.append([row + 1, col])
							if valid_cell(row - 1, col):
								block_passage_list.append([row - 1, col])
							if valid_cell(row, col + 1):
								block_passage_list.append([row, col + 1])
							if valid_cell(row, col - 1):
								block_passage_list.append([row, col - 1])

							shuffle(block_passage_list)

							for j in block_passage_list:
								potential_passage_list.append(j)

					start_cell = [randint(0, int(ROWS)), randint(0, int(ROWS))]
					potential_passage_list.append([start_cell[0], start_cell[1]])

					while not done:
						for i in range(1, len(potential_passage_list) + 1):
							if randint(0, int(len(passage_list) / 50)) == 0:
								maze_passage(int(potential_passage_list[-i][0]), int(potential_passage_list[-i][1]))
								break

						if not potential_passage_list:
							passage_list.sort()
							pygame.display.update()
							spot = grid[passage_list[0][0] + 1][passage_list[0][1] + 1]
							spot.reset()
							done = True

	pygame.quit()

main(WIN, WIDTH)