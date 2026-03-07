# main.py
from CVProcessor import capture_screen, find_queens_grid, detect_grid_size, extract_board, boards_equal, print_board
from BoardSolver import Solver
import pyautogui, mss, time

# Pause delay
pyautogui.PAUSE = 0

def click_queens(bbox, n, solution, time_delay=0):
    x, y, w, h = bbox
    cell_w, cell_h = w / n, h / n

    solution = sorted(solution, key=lambda x: x[0])
    for row, col in solution:
        cx = int(x + (col + 0.5) * cell_w)
        cy = int(y + (row + 0.5) * cell_h)

        pyautogui.doubleClick(cx, cy)
        #time.sleep(time_delay)

def main():
    print("Monitoring screen for LinkedIn Queens puzzle... (Ctrl+C to stop)\n")
    last_board = None

    with mss.mss() as sct:
        while True:
            startTime = time.time()

            img = capture_screen(sct)

            bbox = find_queens_grid(img)
            if bbox is None: 
                continue

            n = detect_grid_size(img, bbox)
            if n is None:
                continue

            board = extract_board(img, bbox, n) # The board as a matrix of chars

            if not boards_equal(board, last_board): # If the board is diff from the last one
                print(f"── Detected {n}×{n} Queens board ──")
                print_board(board)
                print(flush=True)
                last_board = board

                # Solve it and click it
                solver = Solver(n)
                solution = solver.solve(board)
                if not solution:
                    continue
                click_queens(bbox, n, solution)
                print(f"Total Time: {time.time()-startTime:.3f}s")
                # break # In case there's more puzzles

if __name__ == "__main__":
    main()