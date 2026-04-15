import random
import copy

# Check if placing num is valid
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[br + i][bc + j] == num:
                return False
    return True


# Get possible values for a cell
def get_domain(board, row, col):
    return [n for n in range(1, 10) if is_valid(board, row, col, n)]


# Select cell with minimum domain (MRV)
def select_cell(board):
    min_len, best = 10, None
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                d = get_domain(board, i, j)
                if len(d) < min_len:
                    min_len = len(d)
                    best = (i, j)
    return best


# Check for dead-end (forward checking)
def forward_check(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0 and not get_domain(board, i, j):
                return False
    return True


# Solve using backtracking + MRV + forward checking
def solve(board):
    cell = select_cell(board)
    if not cell:
        return True
    row, col = cell
    for num in get_domain(board, row, col):
        board[row][col] = num
        if forward_check(board) and solve(board):
            return True
        board[row][col] = 0
    return False


# Difficulty settings
DIFFICULTY_CLUES = {"Easy": 46, "Medium": 32, "Hard": 26, "Expert": 22}


# Fill full valid board
def fill_board(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for n in nums:
                    if is_valid(board, r, c, n):
                        board[r][c] = n
                        if fill_board(board):
                            return True
                        board[r][c] = 0
                return False
    return True


# Generate puzzle
def generate_sudoku(difficulty="Medium"):
    board = [[0] * 9 for _ in range(9)]
    fill_board(board)
    to_remove = 81 - DIFFICULTY_CLUES.get(difficulty, 32)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    for r, c in cells[:to_remove]:
        board[r][c] = 0
    return board


# Get solved board
def get_solution(original):
    tmp = copy.deepcopy(original)
    solve(tmp)
    return tmp


# Print board with colors
def print_board(board, original, solution):
    print()
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            print("------+-------+------")
        line = ""
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                line += "| "
            if val == 0:
                line += ". "
            elif original[i][j] != 0:
                line += f"\033[93m{val}\033[0m "
            elif val == solution[i][j]:
                line += f"\033[94m{val}\033[0m "
            else:
                line += f"\033[91m{val}\033[0m "
        print(line)
    print()


# Manual play mode
def manual_solve(board, original, solution):
    while True:
        print_board(board, original, solution)

        empty = sum(board[r][c] == 0 for r in range(9) for c in range(9))
        if empty == 0:
            break

        cmd = input("> ").strip().lower()

        if cmd == "quit":
            break
        elif cmd == "hint":
            empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
            if empties:
                r, c = random.choice(empties)
                board[r][c] = solution[r][c]
        else:
            try:
                r, c, num = map(int, cmd.split())
                r, c = r - 1, c - 1
                if original[r][c] == 0:
                    board[r][c] = num
            except:
                pass


# Main
if __name__ == "__main__":
    diff = input("Choose difficulty [Medium]: ").strip().capitalize() or "Medium"
    if diff not in DIFFICULTY_CLUES:
        diff = "Medium"

    original = generate_sudoku(diff)
    board = copy.deepcopy(original)
    solution = get_solution(original)

    print_board(board, original, solution)

    mode = input("Choose mode (1=Manual, 2=AI): ").strip() or "1"

    if mode == "2":
        work = copy.deepcopy(board)
        if solve(work):
            print_board(work, original, solution)
    else:
        manual_solve(board, original, solution)
