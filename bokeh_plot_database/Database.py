# project name: pyranometer
# created by diego aliaga daliaga_at_chacaltaya.edu.bo
from collections import OrderedDict

import datetime
import sqlalchemy as sa
import sqlalchemy.sql as sql
from bokeh.models import ColumnDataSource, LinearAxis
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
        # region defaults
        self.column_data_source = None
        self.dic = dic
        self.table_name = None
        self.user = None
        self.psw = None
        self.ip = None
        self.database_name = None
        self.user_plot = user_plot
        self.time_column_name = 'datetime'
        self.time_int_or_datetime = 'datetime'
        self.y_columns = self.dic['y_columns']
        self.all_y_columns = False
        # endregion
        for key in self.dic.keys():
            setattr(self, key, self.dic[key])

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
        self.y_columns_orm = OrderedDict()

        if self.all_y_columns:
            all_cols_names = self.table.__table__.c.keys()
            all_cols_names.remove(self.time_column_name)
            # logger.debug('all_cols is %s',all_cols_names)
            self.y_columns = OrderedDict()
            for col in all_cols_names:
                # logger.debug('col is %s',col)
                self.y_columns[col] = {
                    'sql_name': col,
                    'show_name': col,
                    'color': 'black',
                    'units': ''
                }

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

        if self.time_int_or_datetime is 'datetime':
            query = sql.func.unix_timestamp(self.time_column)
            logger.debug('considering time type as datetime %s', )
        elif self.time_int_or_datetime is 'int':
            logger.debug('considering time type as int %s', )
            query = self.time_column
        else:
            raise

        query = (
            query / data_average_secs
        )

        query = (
            sql.func.round(query) * data_average_secs +
            utc_offset_seconds
        )
        query = sql.func.from_unixtime(
            sql.func.avg(query)
        )
        query = query.label(self.time_column.key)

        return query

    def group_round_datetime_query(self):
        data_average_secs = self.user_plot.data_average_secs

        if self.time_int_or_datetime is 'datetime':
            query = sql.func.unix_timestamp(self.time_column)
        elif self.time_int_or_datetime is 'int':
            query = self.time_column
        else:
            raise

        query = sql.func.from_unixtime(
            sql.func.round(query / data_average_secs) *
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
        if self.time_int_or_datetime is 'datetime':
            query = query.filter(
                self.user_plot.start_datetime_utc < self.time_column,
                self.time_column < self.user_plot.end_datetime_utc
            )

        elif self.time_int_or_datetime is 'int':
            query = query.filter(
                sql.func.unix_timestamp(self.user_plot.start_datetime_utc) <
                self.time_column
                ,
                self.time_column <
                sql.func.unix_timestamp(self.user_plot.end_datetime_utc)
            )
        # self.eng.echo = True
        self.dataframe = pd.read_sql(query.statement,
                                     self.session.bind)
        # logger.debug('dataframe is %s', self.dataframe)

        # result = query.all()
        # self.dataframe = pd.DataFrame(
        #         result,
        #         columns=(
        #             [self.time_column_name] +
        #             self.y_columns.keys()
        #         )
        # )
        if self.user_plot.plot_type is 'ceil':
            self.set_ceil_data_source()
        elif self.user_plot.plot_type is 'normal':
            self.set_normal_data_source()
        else:
            raise

    def set_normal_data_source(self):
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
            self.column_data_source.data = \
                self.column_data_source._data_from_df(self.dataframe)

    def set_ceil_data_source(self):
        logger.debug('setting up ceil data source %s', )
        data = self.dataframe
        ll = len(data)
        dd = []
        tt = []
        y = []
        dw = []
        dh = []
        time_int = max(self.user_plot.data_average_secs, 30)

        for i in range(ll):
            dd.append(data.iloc[i:i + 1, 1:].T.values)
            tt.append(
                # int(data.iloc[i, 0]) * 1000 - time_int * 1000 / 2
                data.iloc[i, 0].to_datetime() - datetime.timedelta(seconds=time_int / 2)
            )
            y.append(0)
            dw.append(time_int * 1000)
            dh.append(250 * 15)

        ddata={
            'x': tt,
            'y': y,
            'dh': dh,
            'dw': dw,
            'image': dd
        }

        # length_data = len(self.dataframe)
        # data = dict(
        #         x=(self.dataframe[self.time_column_name].astype(np.int64) / 10 ** 6).values.tolist(),
        #         image=self.dataframe.iloc[:, 1:].values.tolist(),
        #         dw=[self.user_plot.data_average_secs] * length_data,
        #         dh=[250 * 15] * length_data,
        #         y=[0] * length_data,
        # )
        # df = pd.DataFrame([],columns=['time','image','dh','dw','y'])
        # df['time'] = self.dataframe[self.time_column_name].astype(np.int64)/10**6
        # df['image'] = self.dataframe.iloc[:,1:]
        # df['dh'] = 250 * 15
        # df['dw'] = self.user_plot.data_average_secs
        # df['y'] = 0

        if self.column_data_source is None:
            self.column_data_source = ColumnDataSource(data=ddata)
        else:
            self.column_data_source.data = ddata

        self.dataframe.replace(np.nan, 'NaN', True)
        # logger.debug('max are %s', self.dataframe.max())
