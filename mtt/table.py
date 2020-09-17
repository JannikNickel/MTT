"""Module that can be used to load/store/modify/request tabular data"""
from .log import log, log_type
import csv
import prettytable

class table():
    def __init__(self, name=""):
        self._name = name
        self._columns = [] #Type: column
        self._data = [] #Type: [cell], [row][column] order
        self._row_count = 0
        self._column_count = 0

    #Properties
    @property
    def name(self):
        return self._name

    @property
    def row_count(self):
        return self._row_count

    @property
    def column_count(self):
        return self._column_count

    #Overrides
    def __getitem__(self, rc):
        column, row = rc
        return self._data[row][column]

    def __setitem__(self, rc, value):
        column, row = rc
        self._data[row][column] = value

    def __str__(self):
        t = prettytable.PrettyTable([x.name for x in self._columns])
        for row in self._data:
            t.add_row([r for r in row])
        return str(t)

    #Utility
    @property
    def format(self):
        t = prettytable.PrettyTable([x.name for x in self._columns])
        return str(t)

    #Get/Set data
    def get(self, column_name, row_index):
        ci = self.column_index(column_name)
        return self._data[row_index][ci]

    def column_index(self, column_name):
        for i in range(self._column_count):
            if self._columns[i].name == column_name:
                return i
        return -1

    def column_name(self, column_index):
        return self._columns[column_index].name

    def column_meta(self, column_name):
        ci = self.column_index(column_name)
        if ci == -1:
            return None
        return self._columns[ci].meta

    def has_column(self, column_name):
        return self.column_index(column_name) != -1

    #Modify shape
    def add_column(self, column_name, column_meta=None):
        self.insert_column(self._column_count, column_name, column_meta)

    def insert_column(self, index, column_name, column_meta=None):
        self._column_count += 1
        cd = column(column_name, column_meta)
        self._columns.insert(index, cd)
        for i in range(self._row_count):
            self._data[i].insert(index, "")

    def add_rows(self, amount):
        for i in range(amount):
            self.add_row()

    def add_row(self, values=None):
        self.insert_row(self._row_count, values)

    def insert_row(self, index, values):
        self._row_count += 1
        v = values[:] if values != None else None #Shallow copy
        if v == None:
            v = ["" for i in range(self._column_count)]
        elif len(v) != self._column_count:
            log("len(values) is not equal to the column count! Filling row with default cells.", log_type.WARNING)
            v = ["" for i in range(self._column_count)]
        self._data.insert(index, v)

    def remove_row(self, index):
        del self._data[index]
        self._row_count -= 1
        for c in self._columns:
            if c.meta != None:
                try:
                    c.meta.removed_row(index)
                except:
                    pass

    #Queries
    def where_value(self, column, value):
        ci = self.column_index(column)
        if ci == -1:
            return []
        return [i for i in range(self._row_count) if self._data[i][ci] == value]

    def where_first(self, column, value):
        ci = self.column_index(column)
        if ci == -1:
            return -1
        for i in range(self._row_count):
            if self._data[i][ci] == value:
                return i
        return -1

    def where_func(self, column, func):
        ci = self.column_index(column)
        if ci == -1:
            return []
        return [i for i in range(self._row_count) if func(self._data[i][ci])]

    def group_by(self, column, func=None, limited_rows=None):
        ci = self.column_index(column)
        if ci == -1:
            return {}
        values = dict()

        r = range(self._row_count)
        if limited_rows != None:
            r = limited_rows

        if func == None:
            func = lambda x: x

        for i in r:
            row = self._data[i]
            cell = func(row[ci])
            if cell in values:
                values[cell].append(i)
            else:
                values[cell] = [i]

        return values

    #Modifications
    def map_column_values(self, column, func=None):
        ci = self.column_index(column)
        if ci == -1:
            return

        if func == None:
            func = lambda x: x

        for i in range(self._row_count):
            cell = self._data[i][ci]
            self._data[i][ci] = func(cell)

    def map_column_values_from(self, other_table, other_column, column, func=None):
        ci = self.column_index(column)
        if ci == -1:
            return

        other_ci = other_table.column_index(other_column)
        if other_ci == -1:
            return

        if func == None:
            func = lambda x: x

        for i in range(self._row_count):
            cell = (other_table._data[i][other_ci])
            self._data[i][ci] = func(cell)

    def map_from_many(self, other_table, other_columns, column, func=None):
        ci = self.column_index(column)
        if ci == -1:
            return

        other_ci = [other_table.column_index(x) for x in other_columns]
        if -1 in other_ci:
            return

        if func == None:
            func = lambda x: x[0]

        for i in range(self._row_count):
            self._data[i][ci] = func([other_table._data[i][k] for k in other_ci])

    def fill_column(self, column, value):
        ci = self.column_index(column)
        if ci == -1:
            return

        for i in range(self._row_count):
            self._data[i][ci] = value

    def fill_column_array(self, column, values):
        ci = self.column_index(column)
        if ci == -1:
            return

        for i in range(self._row_count):
            if i < len(values):
                self._data[i][ci] = values[i]

    #Load/Save
    @staticmethod
    def load_csv(path, delim=","):
        result = table()
        
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=delim)
            lineCount = 0
            for row in reader:
                if lineCount == 0:
                    result._column_count = len(row)
                    result._columns = [column(col) for col in row]
                else:
                    result._data.append(row)
                lineCount += 1
                
        result._row_count = len(result._data)

        #Validate data amount
        for row in result._data:
            if len(row) != result._column_count:
                log("Table " + result.name + "contains a row with an invalid amount of values!", log_type.WARNING)
                break

        return result

    def store(self, path, delim=","):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=delim)
            writer.writerow([column.name for column in self._columns])
            for row in self._data:
                writer.writerow(row)
        

class column():
    def __init__(self, name="", meta=None):
        self._name = name
        self._meta = meta

    @property
    def name(self):
        return self._name

    @property
    def meta(self):
        return self._meta