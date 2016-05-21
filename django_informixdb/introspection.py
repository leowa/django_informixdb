from django.db.backends.base.introspection import (
    BaseDatabaseIntrospection, FieldInfo, TableInfo)

from .datatypes import *


class DatabaseIntrospection(BaseDatabaseIntrospection):
    # Map type codes to Django Field types.
    data_types_reverse = {
        SQL_TYPE_BYTE: 'BinaryField',
        SQL_TYPE_CHAR: 'CharField',
        SQL_TYPE_DATE: 'DateField',
        SQL_TYPE_DATETIME: 'DateTimeField',
        SQL_TYPE_REAL: 'FloatField',
        SQL_TYPE_SMFLOAT: 'FloatField',
        SQL_TYPE_DECIMAL: 'DecimalField',
        SQL_TYPE_NUMERIC: 'DecimalField',
        SQL_TYPE_FLOAT: 'FloatField',
        SQL_TYPE_DOUBLE: 'FloatField',
        SQL_TYPE_INTEGER: 'IntegerField',
        SQL_TYPE_MONEY: '??',
        SQL_TYPE_INTERVAL: '??',
        SQL_TYPE_SERIAL: 'AutoField',
        SQL_TYPE_SMALLINT: 'SmallIntegerField',
        SQL_TYPE_TEXT: 'TextField',
        SQL_TYPE_VARCHAR: 'CharField',
        SQL_TYPE_MASK: '??',
    }

    ignored_tables = []

    def get_table_list(self, cursor):
        cursor.execute('SELECT tabname, tabtype FROM systables')
        return [TableInfo(x[0], x[1].lower()) for x in cursor.fetchall()]

    def get_table_description(self, cursor, table_name):
        "Returns a description of the table, with the DB-API cursor.description interface."
        query_format = """SELECT c.* FROM syscolumns c JOIN systables t
                        ON c.tabid=t.tabid WHERE t.tabname='{}'"""
        cursor.execute(query_format.format(table_name))
        columns = [[c[0], c[3] % 256, None, c[4], c[4], None, 0 if c[3] > 256 else 1]
                   for c in cursor.fetchall()]
        items = []
        for column in columns:
            if column[1] in [SQL_TYPE_NUMERIC, SQL_TYPE_DECIMAL]:
                column[4] = int(column[3] / 256)
                column[5] = column[3] - column[4] * 256
            items.append(FieldInfo(*column))
        return items

    def get_key_columns(self, cursor, table_name):
        key_columns_query = """
        select col1.colname as column_name,
               t2.tabname as referenced_table_name,
               col2.colname as referenced_column
        from systables t1
        join syscolumns col1 on t1.tabid = col1.tabid
        join sysindexes idx1 on idx1.tabid=t1.tabid and col1.colno = idx1.part1
        join sysconstraints const1 on idx1.idxname = const1.idxname and const1.tabid = t1.tabid
        join sysreferences  ref on ref.constrid = const1.constrid
        join sysconstraints const2 on ref.primary = const2.constrid
        join sysindexes idx2 on idx2.idxname = const2.idxname
        join syscolumns col2 on col2.colno = idx2.part1 and col2.tabid = idx2.tabid
        join systables t2 on t2.tabid = idx2.tabid
        where const1.constrtype='R' and t1.tabname ='{}'
        """
        cursor.execute(key_columns_query.format(table_name))
        return cursor.fetchall()

    def get_indexes(self, cursor, table_name):
        """ This query retrieves each index on the given table, including the
            first associated field name """
        index_query = """
        select sc.colname, idx.idxtype, scs.constrtype
         from systables st join sysindexes idx  on st.tabid = idx.tabid
          join syscolumns sc on idx.part1=sc.colno and sc.tabid = st.tabid
          left join sysconstraints scs on idx.idxname = scs.idxname
          where st.tabname='{}' and idx.part2 = 0"""
        cursor.execute(index_query.format(table_name))
        indexes = {}
        for row in cursor.fetchall():
            indexes[row[0]] = {
                'primary_key': True if row[2] == 'P' else False,
                'unique': True if row[1] == 'U' else False
            }
        return indexes

    def _get_col_index(self, cursor, table_name):
        """Private method. Getting Index position of column by its name"""
        col_query = """
            select colno, colname from syscolumns sc
            join systables st on sc.tabid=st.tabid
            where st.tabname='{}'"""
        cursor.execute(col_query.format(table_name))
        return {row[1]: int(row[0]) - 1 for row in cursor.fetchall()}

    def get_relations(self, cursor, table_name):
        """
        Returns a dictionary of {field_index: (field_index_other_table, other_table)}
        representing all relationships to the given table. Indexes are 0-based.
        """
        relations = {}
        key_columns = self.get_key_columns(cursor, table_name)
        for rel in key_columns:
            row0 = self._get_col_index(cursor, table_name)[rel[0]]
            row1 = self._get_col_index(cursor, rel[1])[rel[2]]
            row2 = rel[1]
            relations[row0] = (row1, row2)
        return relations

    def get_constraints(self, cursor, table_name):
        constraints = {}
        index_query = """
        select idxname, idxtype, indexkeys
        from sysindices idx join systables st
         on idx.tabid = st.tabid
        where st.tabname = '{}'"""

        # reverse name, and index here
        all_columns = {v: k for k, v in self._get_col_index().items()}
        cursor.execute(index_query.format(table_name))
        for name, idx_type, keys in cursor.fetchall():
            # keys are in the format like "1 [1], 4 [1], 7 [1]",
            # which means including column #1, #4, and #7
            columns = [all_columns[k.strip().split()[0]] for k in keys.split(',')]
            constraints[name] = {
                'columns': columns,
                'primary_key': len(columns) == 1 and idx_type == 'U',
                'unique': idx_type == 'U',
                'foreign_key': None,
                'check': True,
                'index': idx_type == 'D'
            }
        return constraints
