import random
import copy

# Sudoku Core (CSP + MRV)


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


def get_domain(board, row, col):
    return [n for n in range(1, 10) if is_valid(board, row, col, n)]


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


def forward_check(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0 and not get_domain(board, i, j):
                return False
    return True


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


# Sudoku Generator

DIFFICULTY_CLUES = {"Easy": 46, "Medium": 32, "Hard": 26, "Expert": 22}


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


def generate_sudoku(difficulty="Medium"):
    board = [[0] * 9 for _ in range(9)]
    fill_board(board)
    to_remove = 81 - DIFFICULTY_CLUES.get(difficulty, 32)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    for r, c in cells[:to_remove]:
        board[r][c] = 0
    return board



# Display & Manual Play


YELLOW = "\033[93m"   
BLUE   = "\033[94m"   
RED    = "\033[91m"  
RESET  = "\033[0m"


def get_solution(original):
    tmp = copy.deepcopy(original)
    solve(tmp)
    return tmp


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
                line += f"{YELLOW}{val}{RESET} "   
            elif val == solution[i][j]:
                line += f"{BLUE}{val}{RESET} "    
            else:
                line += f"{RED}{val}{RESET} "      
        print(line)
    print()


def manual_solve(board, original, solution):
    print("\nEnter moves as: row col num  (1-indexed)")
    print("Commands: 'hint', 'quit'\n")

    while True:
        print_board(board, original, solution)

        empty = sum(board[r][c] == 0 for r in range(9) for c in range(9))
        if empty == 0:
            wrong = sum(
                board[r][c] != solution[r][c]
                for r in range(9) for c in range(9)
                if original[r][c] == 0
            )
            if wrong == 0:
                print("Congratulations — puzzle solved correctly!")
            else:
                print(f" Board is full but {wrong} cell(s) are wrong (shown in red).")
            break

        cmd = input("> ").strip().lower()

        if cmd == "quit":
            break
        elif cmd == "hint":
            empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
            if empties:
                r, c = random.choice(empties)
                board[r][c] = solution[r][c]
                print(f"💡 Hint: placed {solution[r][c]} at row {r+1}, col {c+1}")
        else:
            try:
                parts = cmd.split()
                r, c, num = int(parts[0]) - 1, int(parts[1]) - 1, int(parts[2])
                if not (0 <= r < 9 and 0 <= c < 9 and 1 <= num <= 9):
                    print("  Values must be row 1-9, col 1-9, num 1-9.")
                elif original[r][c] != 0:
                    print("  That's a given cell — you can't edit it.")
                else:
                    board[r][c] = num   
            except (ValueError, IndexError):
                print("  Invalid input. Use: row col num  (e.g. 3 5 7)")


# Main


if __name__ == "__main__":
    print("Difficulties: Easy, Medium, Hard, Expert")
    diff = input("Choose difficulty [Medium]: ").strip().capitalize() or "Medium"
    if diff not in DIFFICULTY_CLUES:
        diff = "Medium"

    original = generate_sudoku(diff)
    board    = copy.deepcopy(original)
    solution = get_solution(original)  
    print(f"\n📋 Puzzle ({diff}):")
    print_board(board, original, solution)

    print("Modes: (1) Manual  (2) AI Solve")
    mode = input("Choose mode [1]: ").strip() or "1"

    if mode == "2":
        work = copy.deepcopy(board)
        print("\n🤖 AI solving...")
        if solve(work):
            print(" Solved!")
            print_board(work, original, solution)
        else:
            print("❌ No solution found.")
    else:
        manual_solve(board, original, solution)