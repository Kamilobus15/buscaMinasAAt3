import math
import random
import heapq

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


def random_player():
    options = []
    for i in range(ROWS):
        for j in range(COLUMNS):
            if MATRIX[i][j] == '?':
                options.append((i, j))
    rand_square = options[random.randint(0, len(options))]

    p, q = rand_square

    if (p >= ROWS or q >= COLUMNS) or (p < 0 or q < 0):
        return random_player()

    #print(f'Random player plays {rand_square}')
    print(f'Random player plays {rand_square}')
    return rand_square
    # NO SE PUEDE REVISAR  MINES!!!



    

def brute_force(first, square = None):
    options = []
    if first:
        for i in range(ROWS):
            for j in range(COLUMNS):
                if MATRIX[i][j] != '?':
                    options.append((i, j))
        rand_square = options[random.randint(0, len(options))]
        print(f'Brute force first move {rand_square}')
        return rand_square



    else: #solo agrega a las opciones las casillas que estan al lado de las casillas que ya se han seleccionado
        for i in range(ROWS):
            for j in range(COLUMNS):
                if MATRIX[i][j] != '?':
                    flag((i, j))
                    for p in range(max(0, i - 1), min(ROWS, i + 2)):
                        for q in range(max(0, j - 1), min(COLUMNS, j + 2)):
                            if p != i or q != j:
                                if MATRIX[p][q] == '?':
                                    options.append((p, q))
    if(options == []):
        return random_player()

    rand_square = options[random.randint(0, len(options))]
    while rand_square in FLAGGED:
        rand_square = options[random.randint(0, len(options))]
                    #options.append((i, j))
    print(f'Brute force move {rand_square}')
    return rand_square
    


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
    #print(f'Heuristic move {square}')
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
    create_board()
    #test()

    print('Enter coordinates (ie: 0 3)')

    print("1. Para jugador aleatorio")
    print("2. Para Heurística" )
    print("3. Para Fuerza Bruta")
    input = input('> ')

    
    first = True

    while True:

        print(draw_board())

        if input == '1' or first:
            square = random_player()
        elif input == '2':
            square = heuristic(first)
        elif input == '3':
            square = brute_force(first)
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


