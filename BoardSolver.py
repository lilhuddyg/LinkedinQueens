class Solver:
    
    def __init__(self, n):
        self.board = [["."]*n for _ in range(n)]
        self.n = n
        self.diags = [[1, 1], [1,-1], [-1,1], [-1,-1]]

        
        self.board = [
            ['1', '1', '1', '7', '7', '2', '2'],
['1', '4', '1', '5', '7', '3', '2'],
['4', '4', '1', '5', '3', '3', '2'],
['6', '4', '1', '1', '1', '3', '2'],
['6', '4', '1', '1', '1', '3', '2'],
['4', '4', '4', '1', '3', '3', '3'],
['1', '1', '1', '1', '1', '1', '1']
        ]
        
        # Only for manual testing
        self.n = len(self.board)

    # Iterates through columns recursively, fills in rows with loop
    def solveHelper(self, col, rowsUsed, colorsUsed, placedQueens):
        if len(colorsUsed) == self.n and self.n == len(placedQueens):
            return placedQueens
        
        for row in range(self.n):
            squareColor = self.board[row][col]
            if row not in rowsUsed and squareColor not in colorsUsed and self.diagsFree(row, col, placedQueens):
                # It's a valid square, place and recur
                rowsUsed.add(row)
                colorsUsed.add(squareColor)
                placedQueens.add((row,col))
                result = self.solveHelper(col+1, rowsUsed, colorsUsed, placedQueens)

                # If result is not False, then we found a sol - return it
                if result:
                    return placedQueens
                # Otherwise, we backtrack the move and try another row
                rowsUsed.remove(row)
                colorsUsed.remove(squareColor)
                placedQueens.remove((row,col))
        
        return False
    
    def diagsFree(self, row, col, placedQueens):
        for delta in self.diags:
            newRow = row+delta[0]; newCol = col+delta[1]
            if newRow >= 0 and newRow < self.n and newCol >= 0 and newCol < self.n: # Is within bounds
                if (newRow, newCol) in placedQueens:
                    return False
        return True
        
    def print(self):
        for row in self.board:
            print(row)
        print()

    def solve(self, board=None):
        if board is not None:
            self.board = board
            self.n = len(board)

        #print("This is the raw puzzle:")
        #self.print()  

        res = self.solveHelper(col=0, rowsUsed=set(), colorsUsed=set(), placedQueens=set())
        if not res:
            print("There was no solution findable.")
            return None
        else: #Print the queens with reversed coordinate order
            print("Placed Queens: ", end = "")
            formattedQueens = sorted([[y,x] for x,y in res], key=lambda x: x[0])
            print(formattedQueens)

        toReturn = res

        # Display the solution with Q's in it
        display = [row[:] for row in self.board]  # shallow copy of each row
        for queen in res:
            display[queen[0]][queen[1]] = "Q"
        for row in display:
            print(row)

        return res
        
#solver = Solver(7)
#solver.solve()