#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 16:53:45 2021

@author: adrianferenc
"""
import pandas as pd
import random

from datetime import datetime

#The connect_four_data.csv file contains data collected from running this connect four game with AI vs AI.
def resetData():
    resetter = 'Ej3keN#5'
    areyousure = input('Type '+ resetter + ' to reset data.')
    if areyousure == resetter:
        dict1 = {}
        data = pd.DataFrame([dict1], index=None)
        data.to_csv('connect_four_data.csv')

#This imports the connect_four_data.csv file, saves a backup, and converts to a dataframe. It is quite large, so it takes a while.
print('Game initializing')
data = pd.read_csv('connect_four_data.csv')

data.to_csv(f'connect_four_data_BACKUP_{datetime.now()}.csv')

data_dict = {}
for column in data.columns:
    data_dict[column]=list(data[column])[0]

print('Game initialized')

#This is the class of the game which can be run player vs player, player vs AI (where you can decide who starts), and AI vs AI

class ConnectFour:
    def __init__(self,rows,columns):
        self.rows=rows
        self.columns=columns
        self.board = pd.DataFrame([[' ' for i in range(self.columns) ] for j in range(self.rows)])
        self.turn = 1
        self.available_spaces = self.rows*self.columns
    #Currently the board is shown in the terminal as a dataframe. 
    #TODO: This could have a more compelling gui.
    def showBoard(self):
        print(self.board)
    #Player one's tokens are X's , player two's are O's
    def token(self):
        if self.turn %2 ==1:
            return 'X'
        else:
            return 'O'
    #This puts a token in the given column if the column is not full
    def dropToken(self,column):
        if list(self.board[column]).count(' ') > 0:
            self.board[column][0] = self.token()
    #This reverses the columns
    def flipBoard(self):
        for column in range(self.columns):
            self.board[column] = list(self.board[column])[::-1]
    #This turns the dataframe 90 degrees clockwise
    def rotateRight(self):
        temp_df = pd.DataFrame()
        for row in range(self.rows):
            temp_df[row] = list(self.board.iloc[self.rows-row-1])
        self.board = temp_df
        self.rows = len(self.board.index)
        self.columns = len(self.board.columns)
    #This turns the dataframe 90 degrees counterclockwise 
    def rotateLeft(self):
        temp_df = pd.DataFrame()
        for row in range(self.rows):
            temp_df[row] = list(self.board.iloc[row])[::-1]
        self.board = temp_df
        self.rows = len(self.board.index)
        self.columns = len(self.board.columns)
    #This gets rid of empty spaces between tokens
    def applyGravity(self):
        for column in range(self.columns):
            col = [value for value in list(self.board[column]) if value !=' ']
            while len(col) < self.rows:
                col = [' '] + col
            self.board[column] = col
    #This checks if any row, column, or diagonal has 4 in a row of the same token.
    #TODO this can easily be updated so the number of consecutive tokens is variable.
    def checkWin(self):
        rows = [''.join(list(self.board.iloc[row])) for row in range(self.rows)]
        columns = [''.join(list(self.board[column])) for column in range(self.columns)]
        diagonals = []
        player_one_score = 0
        player_two_score = 0
        maximum = max(self.rows,self.columns)
        for n in range(2*maximum):
            diagonalup = []
            for m in range(maximum):
                try:
                    diagonalup.append(self.board.at[m,n-m])
                except:
                    pass
            diagonals.append(''.join(diagonalup))
        for n in range(-maximum,maximum):
            diagonaldown = []
            for m in range(2*maximum):
                try:
                    diagonaldown.append(self.board.at[n+m,m])
                except:
                    pass
            diagonals.append(''.join(diagonaldown))
        for line in rows+columns+diagonals:
            if 'XXXX' in line:
                player_one_score+=1
            if 'OOOO' in line:
                player_two_score+=1
        if player_one_score + player_two_score > 0:
            if player_one_score > player_two_score:
                return 'X'
            elif player_one_score < player_two_score:
                return 'O'
            else:
                return 'It\'s a tie'
        else:
            return 'There is no winner'
    #This is a list of all possible columns as well as flip, rotate right, and rotate left
    def moveList(self):
        return [str(column) for column in self.board.columns]+['f','r','l']
    #This is used for AI to randomly choose a move in the move list
    def randomChoice(self):
        move_list = self.moveList()
        return random.choice(move_list)
    #This changes the dataframe based on what move is chosen. After all cases, gravity is applied to get rid of spaces.
    def applyMove(self,move):
        if move in [str(column) for column in self.board.columns]:
            self.dropToken(int(move))            
            self.available_spaces -=1
        if move =='f':
            self.flipBoard()
        if move=='r':
            self.rotateRight()
        if move =='l':
            self.rotateLeft()
        self.applyGravity()
    #This is how a real player chooses a move.
    def makeMove(self):
        move = '-1'
        move_list = self.moveList()
        move_string = ', '.join(move_list)[:-1]
        while move not in move_list:
            print(f'Player {self.token()}, it is your turn')
            print('Please select a move from the following list:')
            print(move_string)
            print('')
            print('The numbers represent columns. f is flipping the board, r is rotating right, and l is rotating left')
            move = str(input('What is your move? '))
        return move
    def playGame(self,player_type):
        win_state = self.checkWin()
        #made_moves is used to update the connect_four_data.csv file
        made_moves = dict()
        self.showBoard()
        while (win_state=='There is no winner' and self.available_spaces>0):
            #this initializes the current board in the connect_four_data.csv file if it doesn't exist
            self.dataReader()
            if player_type == 'real':
                move = self.makeMove()
            elif player_type =='VsAI':
                if self.turn%2==1:
                    move = self.makeMove()
                else:
                    move =  self.movePicker()
            elif player_type =='AIVs':
                if self.turn%2==0:
                    move = self.makeMove()
                else:
                    move =  self.movePicker()
            else:
                move = self.movePicker()
            made_moves[str(self.dataColumns())]= move
            self.applyMove(move)
            print('You chose '+ move)
            self.turn+=1
            win_state = self.checkWin()
            print('')
            self.showBoard()
        print('')
        self.dataUpdater(made_moves)
        winning_move = move
        #this line reduces the choices of a given board to only the winning move if that winning move is identified
        data[str(self.dataColumns())] = list(winning_move)
        print(f'The winner is Player {self.checkWin()}')
    #To save space, this converts each column into a number based on it being written in base 3
    def ternaryConverter(self,column):
        converter = {
            ' ': 0,
            'X': 1,
            'O': 2}
        converted = list(pd.Series(column).map(converter))[::-1]
        return sum([3**n*converted[n] for n in range(len(converted))])
    #This returns a list of information that is used as keys in the connect_four_data.csv file. It identifies the number of rows, the who is making a move, and the columns as a list in base 3 (which encodes the number of columns as the length of the list)
    def dataColumns(self):#[rows,token, board in base 3]
        board_in_base_three = [self.ternaryConverter(self.board[column]) for column in self.board.columns]
        column_name = [self.rows,self.token()]+[board_in_base_three]
        return column_name
    #This creates a list of moves for a board that has not been recorded yet in the connect_four_data.csv file
    #TODO Currently it weighs each move equally, but the 'f' 'r' and 'l' moves are surely less significant because they don't add a token to the board. Figuring out the distribution of movesin a new move list seems like it would aid the AI
    def dataReader(self):
        column_name =  str(self.dataColumns())
        if column_name not in data_dict.keys():
            moves = [str(column) for column in self.board.columns]+['f','r','l']
            moves *=10
            data_dict[column_name]= ' '.join(moves)
    #This picks a move randomly from the list of moves.
    def movePicker(self):
        column_name =  str(self.dataColumns())
        moves = data_dict[column_name].split()
        return random.choice(moves)
    #This is what defines the AI. Currently it is very naive and works by taking each move made for each board state. If a player wins, all of their moves are added to the move list, thus making them more likely to be picked. If a player loses, their moves are removed from a move list. This currently will only remove moves if the move list has more than 3 elements. 
    def dataUpdater(self,made_moves):
        for board in made_moves.keys():
            moves = data_dict[board].split()
            if self.token() == board[1]:
                moves.append(made_moves[board])
            if self.token() != board[1] and len(made_moves[board])>3:
                moves.remove(made_moves[board])
            data_dict[board] = ' '.join(moves)


 
#This creates an instance of the game with 6 rows and 7 columns 
c = ConnectFour(6,7)
#This runs the game where you play as player 1 and AI is player 2
c.playGame('VsAI')

#This updates the connect_four_data.csv file after the above game is played
data = pd.DataFrame([data_dict], index=None)
data.to_csv('connect_four_data.csv')