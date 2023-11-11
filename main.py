import math
import random
import heapq
import time
from combinations import integrate_combination_logic

ROWS = 10
COLUMNS = 10
MINE_COUNT = 10

BOARD = []
MINES = set()
EXTENDED = set()

MATRIX = [['?'] * COLUMNS for i in range(ROWS)]

FLAGGED = set()


class Colors(object):
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    ENDC = '\033[0m'


def colorize(s, color):
    return '{}{}{}'.format(color, s, Colors.ENDC)


def get_index(i, j):
    if 0 > i or i >= COLUMNS or 0 > j or j >= ROWS:
        return None
    return i * ROWS + j


def create_board():
    squares = ROWS * COLUMNS

    # Create board
    for _ in range(squares):
        BOARD.append('[ ]')

    # Create mines
    while True:
        if len(MINES) >= MINE_COUNT:
            break
        MINES.add(int(math.floor(random.random() * squares)))


def draw_board():
    lines = []

    for j in range(ROWS):
        if j == 0:
            lines.append('   ' + ''.join(' {} '.format(x) for x in range(COLUMNS)))

        line = [' {} '.format(j)]
        for i in range(COLUMNS):
            line.append(BOARD[get_index(i, j)])
        lines.append(''.join(line))

    return '\n'.join(reversed(lines))


def parse_selection(raw_selection):
    try:
        return [int(x.strip(','), 10) for x in raw_selection.split(' ')]
    except Exception:
        return None


def adjacent_squares(i, j):
    num_mines = 0
    squares_to_check = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            # Skip current square
            if di == dj == 0:
                continue

            coordinates = i + di, j + dj

            # Skip squares off the board
            proposed_index = get_index(*coordinates)
            if not proposed_index:
                continue

            if proposed_index in MINES:
                num_mines += 1

            squares_to_check.append(coordinates)

    return num_mines, squares_to_check


def update_board(square, selected=True):
    i, j = square
    index = get_index(i, j)
    EXTENDED.add(index)


    if index in MINES:
        if not selected:
            return
        BOARD[index] = colorize(' X ', Colors.RED)
        return True
    else:
        num_mines, squares = adjacent_squares(i, j)
        MATRIX[i][j] = num_mines
        if num_mines:
            if num_mines == 1:
                text = colorize(num_mines, Colors.BLUE)
            elif num_mines == 2:
                text = colorize(num_mines, Colors.GREEN)
            else:
                text = colorize(num_mines, Colors.RED)

            BOARD[index] = ' {} '.format(text)
            return
        else:
            BOARD[index] = '   '

            for asquare in squares:
                aindex = get_index(*asquare)
                if aindex in EXTENDED:
                    continue
                EXTENDED.add(aindex)
                update_board(asquare, False)


def reveal_mines():
    for index in MINES:
        if index in EXTENDED:
            continue
        BOARD[index] = colorize(' X ', Colors.YELLOW)
        i, j = divmod(index, ROWS)
        if (i,j) in FLAGGED:
            BOARD[index] = colorize(' X ', Colors.PURPLE)


def has_won():
    return len(EXTENDED | MINES) == len(BOARD)

def get_clues(matrix, rows, columns):
    clues = {}
    for i in range(rows):
        for j in range(columns):
            cell_content = matrix[i][j]
            if cell_content not in ['?', 'F']:  # Asumimos 'F' para celdas con banderas.
                try:
                    # Intenta convertir el contenido de la celda a un número.
                    clue_number = int(cell_content)
                    clues[(i, j)] = clue_number
                except ValueError:
                    # Ignora las celdas que no contienen números convertibles.
                    pass
    return clues


def random_player():
    options = [(i, j) for i in range(ROWS) for j in range(COLUMNS) if MATRIX[i][j] == '?']
    if not options:  # Verifica si la lista de opciones está vacía.
        return None  # Esto puede suceder si el juego ha terminado o si hay un error en la lógica del juego.
    rand_index = random.randint(0, len(options) - 1)  # El rango superior es len(options)-1
    rand_square = options[rand_index]
    print(f'Random player plays {rand_square}')
    return rand_square

    # NO SE PUEDE REVISAR  MINES!!!


def is_valid_move(move, matrix):
    # Un movimiento es válido si la celda está marcada con '?' indicando que no ha sido revelada.
    i, j = move
    return matrix[i][j] == '?'

def find_valid_move(matrix, rows, columns):
    # Encuentra un movimiento válido entre las celdas no reveladas.
    # Selecciona aleatoriamente entre las celdas no reveladas.
    valid_moves = [(i, j) for i in range(rows) for j in range(columns) if matrix[i][j] == '?']
    return random.choice(valid_moves) if valid_moves else None

    

def brute_force(matrix, rows, columns, first):
    start_time = time.time()

    if first:
        # Elige una celda aleatoria para el primer movimiento
        move = (random.randint(0, rows-1), random.randint(0, columns-1))
    else:
        # Obtén las pistas del estado actual del tablero
        clues = get_clues(matrix, rows, columns)

        # Usa la lógica de combinaciones para obtener posibles movimientos seguros
        possible_combinations = integrate_combination_logic(matrix, clues, rows, columns)

        # Selecciona una combinación segura para hacer un movimiento
        move = None
        for combination in possible_combinations:
            for potential_move in combination:
                if matrix[potential_move[0]][potential_move[1]] == '?':
                    move = potential_move
                    break
            if move:
                break

        # Si no se encontraron combinaciones seguras, selecciona una celda aleatoria no revelada
        if not move:
            move = find_valid_move(matrix, rows, columns)

    # Registra el tiempo de ejecución
    end_time = time.time()
    execution_time = end_time - start_time
    with open('resultados.txt', 'a') as f:
        f.write(f'Tiempo de ejecución Fuerza Bruta: {execution_time} segundos\n')

    print(f'Brute force selected move {move} - execution time: {execution_time} seconds')
    return move


#Para la heuristica sera por los que tengan las menores sumas de minas alrededor
class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.sum_of_neighbors = self.calculate_sum_of_neighbors()

    def calculate_sum_of_neighbors(self):
        sum_of_neighbors = 0
        for i in range(max(0, self.row-1), min(ROWS, self.row+2)):
            for j in range(max(0, self.col-1), min(COLUMNS, self.col+2)):
                if i != self.row or j != self.col:
                    if MATRIX[i][j] == '?':
                        sum_of_neighbors += 99 #Las siguientes sumas disminuyen el sesgo a escoger bordes
                        if (i == 0 and j == 0) or (i == 9 and j == 0) or (i == 0 and j == 9) or (i == 9 and j == 9): #Esquinas
                            sum_of_neighbors += 400
                        elif (i == 0 or i == 9) or (j == 0 or j == 9): #bordes normales
                            sum_of_neighbors += 200
                    else:
                        # print(f'Cell {self.row},{self.col} has {i},{j} neighbors')
                        sum_of_neighbors += MATRIX[i][j]*10
        # print(f'Cell {self.row}, {self.col} has sum of neighbors {sum_of_neighbors}')
        # print()
        # print()
        # print()
        return sum_of_neighbors
    
    def returnSum(self):
        return self.sum_of_neighbors
    
    def __le__(self, other):
        return(self.sum_of_neighbors <= other.sum_of_neighbors)
    
    def __lt__(self, other):
        return(self.sum_of_neighbors < other.sum_of_neighbors)


def heuristic(first = True):
    start_time = time.time()
    pq = []
    for i in range(ROWS):
        for j in range(COLUMNS):
            if MATRIX[i][j] == '?':
                cell = Cell(i,j)
                #pq.append(Cell(i,j))
                heapq.heappush(pq, (cell.returnSum(), cell))
            else:
                flag((i,j))
    jugar = heapq.heappop(pq) #pq.pop()
    #square = jugar.row, jugar.col
    square = jugar[1].row, jugar[1].col
    while square in FLAGGED:
        jugar = heapq.heappop(pq)
        square = jugar[1].row, jugar[1].col
    print(f'Heuristic move {square}')
    return square





def flag(square):

    i, j = square
    cant = MATRIX[i][j]
    #print("Revisando {}".format(square) + " con {}".format(cant) + " minas alrededor")
    encontradas = 0

    if(cant != 0):
        for p in range(max(0, i-1), min(ROWS, i+2)):
                for q in range(max(0, j-1), min(COLUMNS, j+2)):
                    if p != i or q != j:
                        if MATRIX[p][q] == '?':
                            encontradas += 1

        #print("Encontradas {}".format(encontradas) + " minas alrededor")
        if encontradas == cant:
            for r in range(max(0, i-1), min(ROWS, i+2)):
                for c in range(max(0, j-1), min(COLUMNS, j+2)):
                    if r != i or c != j:
                        if MATRIX[r][c] == '?' and (r, c) not in FLAGGED:
                            # print(f'Flagging {r} {c}' + " origen {}".format(square))
                            sq = r, c
                            FLAGGED.add(sq)
                            return True



if __name__ == '__main__':
    init = time.time_ns()
    create_board()
    #test()

    print('Enter coordinates (ie: 0 4)')

    print("1. Para jugador aleatorio")
    print("2. Para Heurística" )
    print("3. Para Fuerza Bruta")
    print("4. Para hacerlo 100 veces")
    input = input('> ')

    
    first = True
    #input = '3'
    while True:

        print(draw_board())

        if input == '1' or first:
            square = random_player()
        elif input == '2':
            square = heuristic(first)
        elif input == '3':
            square = brute_force(MATRIX, ROWS, COLUMNS, first)
            first = False
        #square = parse_selection(input('> '))
        if not square or len(square) < 2:
            print('Unable to parse indicies, try again...')
            continue

        mine_hit = update_board(square)
        if mine_hit or has_won():
            if mine_hit:
                reveal_mines()
                print(draw_board())
                print('Game over')
                with open('results.txt', 'a') as f:
                    f.write('Loss\n')
            else:
                print(draw_board())
                print('You won!')
                with open('results.txt', 'a') as f:
                    f.write('Win\n')
            break
    end = time.time_ns()
    print(f' Total time is: {(end - init)}')
    with open('timeBruteForce.txt', 'a') as f:
        f.write(f'{(end - init)}\n')

