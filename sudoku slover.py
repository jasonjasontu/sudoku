
# Include your imports here, if any are used.

import random
import itertools
from copy import deepcopy
import Queue


def sudoku_cells():
    result = set()
    for r, c in itertools.product(range(9), range(9)):
        result.add((r, c))
    return result

def sudoku_arcs():
    result = set()
    for r, c in itertools.product(range(9), range(9)):
        for arc_r in range(9):
            if arc_r != r:
                result.add(((r, c), (arc_r, c)))
        for arc_c in range(9):
            if arc_c != c:
                result.add(((r, c), (r, arc_c)))
        box_r, box_c = r/3, c/3
        for iter_r, iter_c in itertools.product(range(3), range(3)):
            arc_r = box_r*3 + iter_r
            arc_c = box_c*3 + iter_c
            if arc_r == r and arc_c == c: continue
            else: result.add(((r, c), (arc_r, arc_c)))
    return result

def read_board(path):
    board = [[0 for c in range(9)] for r in range(9)]

    line_counter = 0
    f = open(path, 'r')

    for line in f:
        for index in range(9):
            if line[index] != '*':
                board[line_counter][index] = int(line[index])
        line_counter +=1
    return board

class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()
    board = []
    value = [[set() for c in range(9)] for r in range(9)]

    def __init__(self, board):
        self.board = board
        for r, c in itertools.product(range(9), range(9)):
            self.value[r][c] = self.set_values((r, c))

    def set_values(self, cell):
        if self.board[cell[0]][cell[1]] == 0:
            return set([1, 2, 3, 4, 5, 6, 7, 8, 9])
        else:
            return set([self.board[cell[0]][cell[1]]])

    def get_values(self, cell):
        return self.value[cell[0]][cell[1]]

        ##should be improved on this step
#
#        return result


    def remove_inconsistent_values(self, cell1, cell2):
        if self.board[cell2[0]][cell2[1]] == 0:
            return False
        else:
            self.value[cell1[0]][cell1[1]].remove(self.board[cell2[0]][cell2[1]])
            return True

    def infer_ac3(self):
        constricted = False
        while not constricted:
            constricted = True
            for r, c in itertools.product(range(9), range(9)):
                if self.board[r][c] == 0:
                    for arc in self.ARCS:
                        if arc[0] == (r, c) and self.board[arc[1][0]][arc[1][1]] in self.value[r][c]:
                                self.value[r][c].remove(self.board[arc[1][0]][arc[1][1]])
                    if self.value[r][c].__len__() == 1:
                        temp = self.value[r][c].pop()
                        self.board[r][c] = temp
                        self.value[r][c].add(temp)
                        constricted = False
                    elif self.value[r][c].__len__() == 0:
                        return False
        return True

    def infer_improved(self):
        constricted = False
        while not constricted:
            constricted = True
            if not self.infer_ac3():
                return False
            #for row
            for r in range(9):
                #check for each number
                for num in range(1,10):
                    find = False
                    for cell in self.board[r]:
                        if cell == num:
                            find = True
                            break

                    #does not find the number in row
                    if not find:
                        more_than_one = False
                        col_num = -1 #the default for not finding anything yet

                        #check the avalible options for each cell
                        for col in range(9):
                            if num in self.value[r][col]:
                                if not find:
                                    find = True
                                    col_num = col
                                else:
                                    more_than_one = True

                        #handle the result
                        if not find:
                            return False #one raw run out of the options for one number
                        elif not more_than_one:
                            # put the only option in the cell
                            self.board[r][col_num] = num
                            self.value[r][col_num] = set([num])
                            constricted = False

            #for col
            for c in range(9):
                #check for each number
                for num in range(1,10):
                    find = False
                    for row_index in range(9):
                        if self.board[row_index][c] == num:
                            find = True
                            break

                    #does not find the number in col
                    if not find:
                        more_than_one = False
                        raw_num = -1 #the default for not finding anything yet

                        #check the avalible options for each cell
                        for row in range(9):
                            if num in self.value[row][c]:
                                if not find:
                                    find = True
                                    row_num = row
                                else:
                                    more_than_one = True

                        #handle the result
                        if not find:
                            return False #one col run out of the options for one number
                        elif not more_than_one:
                            # put the only option in the cell
                            self.board[row_num][c] = num
                            self.value[row_num][c] = set([num])
                            constricted = False

            #for 3x3 grid
            for big_box_r, big_box_c in itertools.product(range(3), range(3)):
                #check through the numbers
                for num in range(1, 10):
                    find = False
                    for small_box_r, small_box_c in itertools.product(range(3),range(3)):
                        r = big_box_r*3+small_box_r
                        c = big_box_c*3+small_box_c
                        if self.board[r][c] == num:
                            find = True
                            break

                    #does not find the number in box
                    if not find:
                        more_than_one = False
                        cell_num = (-1, -1) #the default for not finding anything yet

                        #check the avalible options for each cell
                        for row, col in itertools.product(range(big_box_r*3,big_box_r*3+3), range(big_box_c*3, big_box_c*3+3)):
                            if num in self.value[row][col]:
                                if not find:
                                    find = True
                                    cell_num = (row, col)
                                else:
                                    more_than_one = True

                        #handle the result
                        if not find:
                            return False #one box run out of the options for one number
                        elif not more_than_one:
                            # put the only option in the cell
                            self.board[cell_num[0]][cell_num[1]] = num
                            self.value[cell_num[0]][cell_num[1]] = set([num])
                            constricted = False
        return True

    def is_solved(self):
        for r, c in itertools.product(range(9), range(9)):
            if self.board[r][c] == 0: return False
        return True

    def find_guessing_cell(self):
        mini = 10
        cell = (-1, -1)
        for r, c in itertools.product(range(9), range(9)):
            if self.board[r][c] > 0: continue
            if self.value[r][c].__len__() < mini:
                cell = (r, c)
                mini = len(self.value[r][c])
        return cell

    def infer_with_guessing(self):
        guessing_record = []
        self.infer_improved()

        while not self.is_solved():

            going_back = False
            need_guessing = True

            while need_guessing:

                #find the cell with least option to start guessing
                cell = self.find_guessing_cell()

                if len(self.value[cell[0]][cell[1]]) == 0:
                    going_back = True
                else:
                    #make a guess
                    temp_num = self.value[cell[0]][cell[1]].pop()
                    guessing_record.append((deepcopy(self.board), deepcopy(self.value)))
                    self.board[cell[0]][cell[1]] = temp_num
                    self.value[cell[0]][cell[1]] = set([temp_num])

                    #improve thes sloving process
                    if self.infer_improved():
                        need_guessing = False
                    else:
                        going_back = True

                #solve and check the conflict
                if going_back:
                    self.board, self.value = guessing_record.pop()
                    going_back = False



