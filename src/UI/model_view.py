import typing
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt

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