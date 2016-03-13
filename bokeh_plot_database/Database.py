# project name: pyranometer
# created by diego aliaga daliaga_at_chacaltaya.edu.bo
import sqlalchemy as sa
import sqlalchemy.sql as sql
from bokeh.models import ColumnDataSource
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import pandas as pd
import numpy as np
import my_logger

logger = my_logger.get_logger(name=__name__, level='DEBUG')


class Database(object):
    """
    a class

    Attributes:
        dic: None
        table: None
        user: None
        psw: None
        ip: None
        database_name: None
        user_plot: None
        time_column_name: None
        url: None
        eng: None
        meta: None
        base: None
        y_columns: None
        y_columns_orm: None
        time_column: None
        session: None
        dataframe: None
        column_data_source: ColumnDataSource()
        max_dataframe: None
        min_dataframe: None
    """

    # class in charge to handle connection to a particular
    # table in a database
    def __init__(self, dic, user_plot):
        self.column_data_source = None
        self.dic = dic
        self.table_name = dic['table']
        self.user = dic['user']
        self.psw = dic['psw']
        self.ip = dic['ip']
        self.database_name = dic['database_name']
        self.user_plot = user_plot
        self.time_column_name = dic['time_column_name']
        self.url = 'mysql://{user}:{psw}@{ip}/{db}'
        self.url = self.url.format(
                user=self.user,
                psw=self.psw,
                ip=self.ip,
                db=self.database_name
        )

        self.eng = sa.create_engine(self.url)

        self.meta = sa.MetaData()

        self.meta.reflect(bind=self.eng,
                          # schema=self.data_base_name,
                          only=[self.table_name])

        self.base = automap_base(metadata=self.meta)
        self.base.prepare()

        self.table = self.base.classes[self.table_name]
        self.y_columns = self.dic['y_columns']
        self.y_columns_orm = dict()
        for col_key in self.y_columns.keys():
            col = self.y_columns[col_key]
            self.y_columns_orm[col_key] = getattr(self.table, col['sql_name'])

        self.time_column = getattr(self.table, self.time_column_name)

        self.session = Session(self.eng)
        self.set_column_data_source()

    def round_datetime_query(self):
        data_average_secs = self.user_plot.data_average_secs
        if self.user_plot.utc_offset_enabled:
            utc_offset_seconds = self.user_plot.utc_offset_hours * 3600
        else:
            utc_offset_seconds = 0
        query = (sql.func.unix_timestamp(self.time_column) /
                 data_average_secs)

        query = (sql.func.round(query) * data_average_secs +
                 utc_offset_seconds)
        query = sql.func.from_unixtime(
                sql.func.avg(query))
        query = query.label(self.time_column.key)

        return query

    def group_round_datetime_query(self):
        data_average_secs = self.user_plot.data_average_secs
        query = sql.func.from_unixtime(
                sql.func.round(
                        sql.func.unix_timestamp(self.time_column) /
                        data_average_secs) *
                data_average_secs
        )

        return query

    def y_column_queries(self):
        queries = []
        for y_name in self.y_columns_orm.keys():
            query = sql.func.avg(self.y_columns_orm[y_name])
            query = query.label(self.y_columns_orm[y_name].key)
            queries.append(query)
        return queries

    def set_column_data_source(self):
        group_round_datetime_query = self.group_round_datetime_query()
        round_datetime_query = self.round_datetime_query()
        y_queries = self.y_column_queries()
        queries = [round_datetime_query] + y_queries
        query = self.session.query(*queries)
        query = query.group_by(group_round_datetime_query)
        query = query.filter(self.user_plot.start_datetime_utc <
                             self.time_column,
                             self.time_column <
                             self.user_plot.end_datetime_utc
                             )

        # self.dataframe = pd.read_sql(query.statement,
        #                              self.session.bind)

        result = query.all()
        self.dataframe = pd.DataFrame(
                result,
                columns=(
                    [self.time_column_name] +
                    self.y_columns.keys()
                )
        )

        columns_dic = self.dic['y_columns']
        for col_key in columns_dic.iterkeys():
            if 'function' in columns_dic[col_key]:
                xxx = self.dataframe[col_key]
                function = columns_dic[col_key]['function']
                function = function.replace('x', 'xxx')
                self.dataframe[col_key] = eval(function)

        self.max_dataframe = self.dataframe.max()
        self.min_dataframe = self.dataframe.min()
        # logger.debug('max are %s', self.dataframe.max())

        self.dataframe.replace(np.nan, 'NaN', True)
        # logger.debug('max are %s', self.dataframe.max())
        if self.column_data_source is None:
            self.column_data_source = ColumnDataSource(data=self.dataframe)
        else:
            self.column_data_source.data = (
                ColumnDataSource(data=self.dataframe).data)
