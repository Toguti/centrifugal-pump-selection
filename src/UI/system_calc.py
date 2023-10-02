from PyQt6.QtCore import (Qt, 
                          QSize, 
                          QAbstractTableModel
                          )
from pressure_drop.local_loss import *
from pressure_drop.total_head_loss import *


class InputTable(QAbstractTableModel):
    def __init__(self, data):
        super(InputTable, self).__init__()
        self._data = data

    def data (self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        

    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self,index):
        return len(self._data[0])