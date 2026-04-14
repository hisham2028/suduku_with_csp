import random   # Used to shuffle number lists during board generation and pick random hint cells
import copy     # Used to create deep copies of the board (fully independent clones, not references)

# ==============================
# Sudoku Core (CSP + MRV)
# ==============================
# CSP = Constraint Satisfaction Problem (row/col/box uniqueness rules are the "constraints")
# MRV = Minimum Remaining Values heuristic (always pick the cell with fewest legal options)


def is_valid(board, row, col, num):
    """
    Checks whether placing 'num' at board[row][col] violates any Sudoku rule.
    Returns True if the placement is legal, False if it breaks a constraint.
    """

    for i in range(9):                          # Loop through all 9 positions in the row AND column
        if board[row][i] == num:                # 'num' already exists somewhere in this row
            return False
        if board[i][col] == num:                # 'num' already exists somewhere in this column
            return False

    br = 3 * (row // 3)                         # Top-left ROW of the 3x3 box containing (row,col)
                                                # row // 3 gives box index (0,1,2); multiply by 3 for actual row
    bc = 3 * (col // 3)                         # Top-left COLUMN of the 3x3 box containing (row,col)

    for i in range(3):                          # Iterate over 3 rows within the box
        for j in range(3):                      # Iterate over 3 columns within the box
            if board[br + i][bc + j] == num:    # 'num' already exists somewhere in this 3x3 box
                return False

    return True                                 # Passed all three constraint checks → placement is valid


def get_domain(board, row, col):
    """
    Returns the list of numbers (1–9) that can legally be placed at board[row][col].
    This is the "domain" of the cell in CSP terminology.
    """
    return [n for n in range(1, 10) if is_valid(board, row, col, n)]
    # List comprehension: for every digit 1–9, include it only if is_valid says it's legal


def select_cell(board):
    """
    MRV Heuristic: scans all empty cells and returns the one with the
    SMALLEST domain (fewest legal values). Choosing the most constrained
    cell first reduces the branching factor and speeds up solving significantly.
    Returns None if there are no empty cells (board is complete).
    """

    min_len = 10        # Start higher than any possible domain size (max domain = 9)
    best = None         # Will hold the (row, col) of the most constrained empty cell

    for i in range(9):                              # Loop over all rows
        for j in range(9):                          # Loop over all columns
            if board[i][j] == 0:                    # Only consider EMPTY cells (0 = empty)
                d = get_domain(board, i, j)         # Get legal digits for this cell
                if len(d) < min_len:                # If this cell is more constrained than current best
                    min_len = len(d)                # Update minimum domain size found so far
                    best = (i, j)                   # Record this cell as the new best candidate

    return best     # Returns (row, col) of most constrained cell, or None if board is full


def forward_check(board):
    """
    After a digit is placed, scans ALL remaining empty cells to verify that
    none of them has become impossible (domain = empty set).
    If any empty cell has zero legal values, this branch is already unsolvable —
    return False immediately so the solver can backtrack without going deeper.
    """

    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:                    # Only check empty cells
                if not get_domain(board, i, j):     # If domain is empty (no legal values exist)
                    return False                    # Dead end — this branch can never lead to a solution

    return True     # All empty cells still have at least one legal value → branch is still viable


def solve(board):
    """
    Main recursive backtracking solver using MRV + Forward Checking.
    Mutates 'board' in-place.
    Returns True if the puzzle was solved, False if no solution exists.

    Algorithm:
      1. Pick the most constrained empty cell (MRV)
      2. Try each value in its domain
      3. Place the value, run forward check
      4. If viable, recurse
      5. If recursion fails or forward check fails, undo (backtrack)
    """

    cell = select_cell(board)           # Step 1: find best empty cell via MRV
    if not cell:
        return True                     # No empty cells remain → board is fully and correctly filled!

    row, col = cell                     # Unpack the chosen cell coordinates

    for num in get_domain(board, row, col):     # Step 2: try every legal digit for this cell
        board[row][col] = num                   # Step 3: tentatively place the digit

        if forward_check(board) and solve(board):   # Step 4: check viability THEN recurse
            # forward_check runs FIRST due to short-circuit evaluation
            # Only recurse if forward_check passes (avoids wasted recursive calls)
            return True                         # Propagated success up the call stack

        board[row][col] = 0             # Step 5: BACKTRACK — undo placement, try next digit

    return False    # All digits in domain were tried and failed → tell caller to backtrack


# ==============================
# Sudoku Generator
# ==============================

# Maps difficulty name to the number of GIVEN clues (filled cells) left in the puzzle
# More clues = easier (more information given to the player)
DIFFICULTY_CLUES = {"Easy": 46, "Medium": 32, "Hard": 26, "Expert": 22}


def fill_board(board):
    """
    Generates a COMPLETE, valid Sudoku solution by filling every cell.
    Uses randomized backtracking (shuffles digits before trying them)
    so each call produces a different board layout.

    Unlike solve(), this iterates left-to-right, top-to-bottom (not MRV),
    because random generation is fast enough without the heuristic.
    """

    for r in range(9):                      # Iterate every row
        for c in range(9):                  # Iterate every column in that row
            if board[r][c] == 0:            # Only fill empty cells
                nums = list(range(1, 10))   # Create list [1, 2, 3, 4, 5, 6, 7, 8, 9]
                random.shuffle(nums)        # Randomize order so boards are unique each run

                for n in nums:              # Try each digit in shuffled order
                    if is_valid(board, r, c, n):    # Check digit doesn't break any constraint
                        board[r][c] = n             # Place the digit
                        if fill_board(board):       # Recurse to fill remaining cells
                            return True             # Entire board filled successfully
                        board[r][c] = 0             # This path failed → backtrack (undo placement)

                return False    # No valid digit found for this cell → tell caller to backtrack

    return True     # All cells filled successfully (loop completed without hitting an empty cell)


def generate_sudoku(difficulty="Medium"):
    """
    Creates a playable Sudoku puzzle at the given difficulty level.
    Steps:
      1. Generate a complete valid board using fill_board()
      2. Remove cells randomly until the desired clue count is reached
    Returns the puzzle board (with 0s for empty cells).

    NOTE: This does NOT guarantee a unique solution — a proper implementation
    would verify uniqueness after each cell removal.
    """

    board = [[0] * 9 for _ in range(9)]             # Create blank 9x9 board (all zeros)
    fill_board(board)                               # Fill it with a complete valid solution

    to_remove = 81 - DIFFICULTY_CLUES.get(difficulty, 32)
    # 81 = total cells; subtract desired clue count to get how many cells to blank out
    # .get(difficulty, 32) uses 32 (Medium) as fallback if difficulty key not found

    cells = [(r, c) for r in range(9) for c in range(9)]   # List all 81 cell coordinates
    random.shuffle(cells)                                   # Randomize removal order

    for r, c in cells[:to_remove]:     # Take the first 'to_remove' cells from shuffled list
        board[r][c] = 0                # Remove that cell (set to empty)

    return board    # Return the puzzle (complete solution with some cells blanked)


# ==============================
# Display & Manual Play
# ==============================

# ANSI escape codes — these are terminal color codes
# When printed, they change text color for the characters that follow
YELLOW = "\033[93m"     # Color for GIVEN clues (pre-filled by puzzle, cannot be changed)
BLUE   = "\033[94m"     # Color for CORRECT user entries (matches the solution)
RED    = "\033[91m"     # Color for WRONG user entries (doesn't match the solution)
RESET  = "\033[0m"      # Resets color back to terminal default (must follow every colored char)


def get_solution(original):
    """
    Computes and returns the complete solved version of the original puzzle.
    Uses a deep copy so the original puzzle board is never modified.
    The solution is computed ONCE and reused throughout the game for validation.
    """

    tmp = copy.deepcopy(original)   # Create a fully independent copy of the original board
    solve(tmp)                      # Solve the copy in-place (mutates tmp, not original)
    return tmp                      # Return the solved board


def print_board(board, original, solution):
    """
    Renders the current Sudoku board to the terminal with:
    - Grid dividers every 3 rows and columns (standard Sudoku formatting)
    - YELLOW for given clues (from original puzzle)
    - BLUE for correct user entries (matches solution)
    - RED for incorrect user entries (doesn't match solution)
    - '.' for empty cells
    """

    print()                         # Blank line before board for spacing

    for i, row in enumerate(board):                     # Loop through rows with index
        if i % 3 == 0 and i != 0:                      # Every 3rd row (but not before row 0)
            print("------+-------+------")             # Print horizontal divider between 3x3 boxes

        line = ""                                       # Build the display string for this row

        for j, val in enumerate(row):                  # Loop through cells in this row with index
            if j % 3 == 0 and j != 0:                  # Every 3rd column (but not before col 0)
                line += "| "                           # Add vertical divider between 3x3 boxes

            if val == 0:                                # Cell is empty
                line += ". "                           # Display as dot
            elif original[i][j] != 0:                  # Cell has a value AND it was a given clue
                line += f"{YELLOW}{val}{RESET} "       # Display in yellow (cannot be changed)
            elif val == solution[i][j]:                 # Cell has a user-entered value that is CORRECT
                line += f"{BLUE}{val}{RESET} "         # Display in blue (right answer)
            else:                                       # Cell has a user-entered value that is WRONG
                line += f"{RED}{val}{RESET} "          # Display in red (wrong answer)

        print(line)     # Print the completed row string

    print()     # Blank line after board for spacing


def manual_solve(board, original, solution):
    """
    The interactive game loop for manual play.
    Accepts commands from the player until the board is full or they quit.

    Supported commands:
      'row col num'  — place a digit (e.g. "3 5 7" = row 3, col 5, digit 7)
      'hint'         — reveal one random empty cell using the solution
      'quit'         — exit the game
    """

    print("\nEnter moves as: row col num  (1-indexed)")    # Instruction message
    print("Commands: 'hint', 'quit'\n")                   # List available commands

    while True:                 # Keep looping until break (solved or quit)
        print_board(board, original, solution)      # Render current board state

        # Count remaining empty cells
        empty = sum(board[r][c] == 0 for r in range(9) for c in range(9))

        if empty == 0:          # No empty cells → board is full
            # Count how many user-filled cells have the wrong value
            wrong = sum(
                board[r][c] != solution[r][c]           # Value doesn't match solution
                for r in range(9) for c in range(9)
                if original[r][c] == 0                  # Only check cells the user filled (not given clues)
            )
            if wrong == 0:
                print("✅ Congratulations — puzzle solved correctly!")  # Perfect solve
            else:
                print(f"❌ Board is full but {wrong} cell(s) are wrong (shown in red).")  # Errors exist
            break               # Exit the game loop either way

        cmd = input("> ").strip().lower()   # Read player input, strip whitespace, lowercase

        if cmd == "quit":
            break               # Player chose to exit

        elif cmd == "hint":
            # Find all remaining empty cells
            empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
            if empties:                                 # Only give hint if empty cells exist
                r, c = random.choice(empties)          # Pick a random empty cell
                board[r][c] = solution[r][c]           # Fill it with the correct value from solution
                print(f"💡 Hint: placed {solution[r][c]} at row {r+1}, col {c+1}")  # Confirm to player

        else:                   # Assume it's a "row col num" move command
            try:
                parts = cmd.split()                     # Split input string into parts by whitespace
                r   = int(parts[0]) - 1                 # Parse row (convert from 1-indexed to 0-indexed)
                c   = int(parts[1]) - 1                 # Parse column (convert from 1-indexed to 0-indexed)
                num = int(parts[2])                     # Parse the digit to place

                if not (0 <= r < 9 and 0 <= c < 9 and 1 <= num <= 9):
                    print("⚠️  Values must be row 1-9, col 1-9, num 1-9.")    # Out of range
                elif original[r][c] != 0:
                    print("⚠️  That's a given cell — you can't edit it.")      # Can't overwrite a clue
                else:
                    board[r][c] = num   # Place the digit (wrong entries are ALLOWED; red color is the feedback)

            except (ValueError, IndexError):
                # ValueError: input wasn't a number (e.g. "abc")
                # IndexError: fewer than 3 parts provided
                print("⚠️  Invalid input. Use: row col num  (e.g. 3 5 7)")


# ==============================
# Main
# ==============================

if __name__ == "__main__":
    # This block only runs when the script is executed directly (not when imported as a module)

    print("Difficulties: Easy, Medium, Hard, Expert")
    diff = input("Choose difficulty [Medium]: ").strip().capitalize() or "Medium"
    # .strip() removes leading/trailing whitespace
    # .capitalize() makes first letter uppercase (e.g. "hard" → "Hard")
    # 'or "Medium"' uses "Medium" if input was blank (empty string is falsy)

    if diff not in DIFFICULTY_CLUES:        # Validate difficulty input
        diff = "Medium"                     # Default to Medium if unrecognised

    original = generate_sudoku(diff)        # Generate the puzzle (with blanked cells)
    board    = copy.deepcopy(original)      # Player's working copy (will be mutated during play)
    solution = get_solution(original)       # Pre-compute the full solution ONCE (reused for all validation)

    print(f"\n📋 Puzzle ({diff}):")
    print_board(board, original, solution)  # Show the starting puzzle

    print("Modes: (1) Manual  (2) AI Solve")
    mode = input("Choose mode [1]: ").strip() or "1"
    # Same pattern: strip whitespace, default to "1" if blank

    if mode == "2":
        work = copy.deepcopy(board)         # Create a separate copy for AI to solve (don't touch original)
        print("\n AI solving...")
        if solve(work):                     # Run the CSP+MRV solver on the copy
            print("✅ Solved!")
            print_board(work, original, solution)   # Display the solved board
        else:
            print("❌ No solution found.")  # Should never happen with a valid generated puzzle

    else:                                   # Default: mode 1 (manual play)
        manual_solve(board, original, solution)     # Hand control to the interactive game loop
