import itertools

def get_frontier_cells(matrix, rows, columns):
    frontier = set()
    for i in range(rows):
        for j in range(columns):
            if matrix[i][j] not in ['?', 'F']:
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < rows and 0 <= nj < columns and matrix[ni][nj] == '?':
                            frontier.add((ni, nj))
    return frontier

def generate_consistent_combinations(frontier, clues, rows, columns):
    def is_consistent(combination):
        for (ci, cj), clue in clues.items():
            count = 0
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    if (ci + di, cj + dj) in combination:
                        count += 1
            if count != clue:
                return False
        return True

    all_combinations = []
    for r in range(1, len(frontier) + 1):
        for combination in itertools.combinations(frontier, r):
            if is_consistent(set(combination)):
                all_combinations.append(set(combination))
    return all_combinations

def integrate_combination_logic(matrix, clues, rows, columns):
    frontier_cells = get_frontier_cells(matrix, rows, columns)
    possible_combinations = generate_consistent_combinations(frontier_cells, clues, rows, columns)
    return possible_combinations

# The following code would be part of the main game loop or a function that is called when needed.
# matrix, clues, rows, and columns would be derived from the game state.

# Example game state (for illustration purposes):
# matrix = [
#     ['1', '?', '?'],
#     ['?', '?', '?'],
#     ['?', '?', '?']
# ]
# clues = {(0, 0): 1}
# rows, columns = 3, 3

# integrated_combinations = integrate_combination_logic(matrix, clues, rows, columns)
# print(integrated_combinations)
