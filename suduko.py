from collections import Counter
from copy import deepcopy
from itertools import count
from traceback import print_exc

#https://www.websudoku.com/?level=4

class SudukoBoard:
    side=3
    sz=side*side
    class Cell:
        def __init__(self,board,row,col):
            self._values= [None] * SudukoBoard.sz
            self._value=None
            self.sets=[]
            self.row=row
            self.col=col
            self.open=SudukoBoard.sz
            self.board=board

        def add_set(self,set):
            self.sets.append(set)

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self,value):
            if self._value is not None and self._value!=value:
                raise ValueError("Conflicting value for cell",self.row,self.col,self._value,value)
            if self._value != value:
                self._value=value
                self._values=[False]*SudukoBoard.sz
                self._values[value-1]=True
                self.open=0
                self.board.open-=1
                for s in self.sets:
                    for c in s.entries:
                        if c!=self:
                            c.cantbe(value)

        def cantbe(self, value):
            if self._values[value - 1] == True:
                raise ValueError("Conflicting cant be for cell, already set",self.row,self.col,self._value,value)
            if self._values[value-1] != False:
                self._values[value-1]=False
                self.open -=1
            cnt=0
            nidx=None
            for idx,v in enumerate(self._values):
                if v is None:
                    cnt+=1
                    nidx=idx
            if cnt==1:
                self.value=nidx+1

        def couldbe(self, value):
            return self._values[value - 1]

        def couldbelist(self):
            return [idx+1 for idx,x in enumerate(self._values) if x is None]

    class Set:
        def __init__(self):
            self.entries=[]

        def add_cell(self,cell):
            self.entries.append(cell)
            cell.add_set(self)

        def update(self,entry):
            value=entry.value
            for other in self.entries:
                if other==entry:
                    continue
                if other.value == value:
                    raise Exception("Illegal value")
                else:
                    other.value=not value

    def __init__(self):
        self.initial=0
        self.open=SudukoBoard.sz**2
        self.cells=[]
        self.rows=[SudukoBoard.Set() for i in range(SudukoBoard.sz)]
        self.cols=[SudukoBoard.Set() for i in range(SudukoBoard.sz)]
        self.blks=[SudukoBoard.Set() for i in range(SudukoBoard.sz)]
        s3=SudukoBoard.side*SudukoBoard.sz
        for i in range(SudukoBoard.sz**2):
            cell=SudukoBoard.Cell(self,i//SudukoBoard.sz,i%SudukoBoard.sz)
            self.cells.append(cell)
        for cell in self.cells:
            self.rows[cell.row].add_cell(cell)
            self.cols[cell.col].add_cell(cell)
            self.blks[(cell.row)//SudukoBoard.side+((cell.col)//SudukoBoard.side)*SudukoBoard.side].add_cell(cell)

    def setup(self,txt):
        trows=txt.split(",")
        if len(trows)!=SudukoBoard.sz:
            raise Exception("Incorrect number of rows")
        cnt=0
        for ridx,trow in enumerate(trows):
            if len(trows) != SudukoBoard.sz:
                raise Exception("Incorrect number of columns row ",ridx)
            for cidx,c in enumerate(trow):
                if c != '.':
                    v=int(c)
                    cnt+=1
                    self.set(ridx,cidx,v)
                    # print("Set ",ridx+1,cidx+1, " tot ",cnt," left ",self.open,
                    #       " auto ",SudukoBoard.sz**2-self.open-cnt)
                    # self.print()

    def set(self,row,col,value):
        self.rows[row].entries[col].value=value

    def print(self):
        for ridx,r in enumerate(self.rows):
            for cidx,c in enumerate(r.entries):
                print("." if c.value is None else c.value,end='')
                if (cidx+1)%SudukoBoard.side == 0:
                    print("|",end='')
            print()
            if (ridx+1)%SudukoBoard.side == 0:
                print("{}".format("-"*(SudukoBoard.sz+SudukoBoard.side)))

    def solve(self,depth=0,guesses=[]):
        for i in range(1000):
            print("Iteration ",depth,i)
            # for c in self.cells:
            #     print(c.row,c.col,c.couldbelist(),c._value,c._values)
            open=[Counter([len(c.couldbelist()) for c in self.cells])]
            print("open cells",open)
            for c in self.cells:
                if c.open!=1:
                    continue
                if c.open != len(c.couldbelist()):
                    pass
                value=c.couldbelist()
                c.set(value)

            if self.open >0 and not 1 in open:
                print("We have to guess depth {} and {} cells open".format(depth,self.open))
                bestguess=[]
                for c in self.cells:
                    for guess in c.couldbelist():
                        other=deepcopy(self)
                        try:
                            other.set(c.row,c.col,guess)
                            bestguess.append((other.open,(c.row,c.col,guess)))
                        except ValueError as e:
                            pass
                        except Exception as e:
                            print_exc()
                for open,(row,col,guess) in sorted(bestguess):
                    print("Best guess ",row,col,guess,depth)
                    other = deepcopy(self)
                    other.set(row,col,guess)
                    soln,soln_guesses = other.solve(depth + 1,guesses+[(row,col,guess)])
                    if soln.open == 0:
                        print("guess return")
                        return soln,soln_guesses
            # if self.open == 0:
            #     print("Solved with {} guesses {}".format(depth,guesses))
            #     self.print()
            return self,guesses



    def leftopen(self):
        cnt=0
        for c in self.cells:
            if c.value is None:
                cnt+=1
        if cnt != self.open:
            assert "BAD"
        return cnt
if __name__ == "__main__":
    board=SudukoBoard()
    evil="..1.4..6.,...8...2.,..4..9.3.,.48..76..,5.......9,..25..47.,.8.1..2..,.5...6...,.6..9.1.."
    evil2="..9..3.14,....96...,.2....9..,..8.....1,..12784..,6.....7..,..7....4.,...93....,46.8..3.."
    medium="8.4.7.6.5,....8237.,7......1.,35...8...,....9....,...4...61,.3......7,.9571....,4.6.3.1.2"
    hard="......1..,7..4.18..,..375..4.,4.1.7....,.9..8..7.,....9.6.5,.6..129..,..45.6..2,..2......"
    easy=".7.4..2..,2..5791..,.4......6,..261.35.,631...427,.54.328..,5......3.,..6157..4,..8..6.1."
    board.setup(evil2)
    board.print()
    print()
    soln,guesses=board.solve()
    print("Final : guesses",guesses)
    soln.print()
    pass