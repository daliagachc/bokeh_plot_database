# project name: pyranometer
# created by diego aliaga daliaga_at_chacaltaya.edu.bo
import datetime
from time import timezone

from bokeh.models import Plot, Range1d, DatetimeAxis, \
    PanTool, WheelZoomTool, \
    CrosshairTool, PreviewSaveTool, \
    ResizeTool, Legend, Line, Image, ColumnDataSource, LinearColorMapper, LinearAxis, DataRange1d

import numpy as np
from bokeh.plotting import Figure

from bokeh_plot_database.UserYColumn import UserYColumn
import my_logger
from bokeh_plot_database.Database import Database

logger = my_logger.get_logger(name=__name__, level='DEBUG')


class UserPlot(object):
    """ A class
    
    Attributes:
        name: None
        user_dic_pars: None
        databases: None
        plot: None
        y_columns: {}
        x_axis: None
        column_data_sources: None
        legends: []
        x_range: None
    """

    # x_ranges_set = False
    # shared_x_ranges = {}
    def __init__(self, dic, name, parameters_dic, shared_ranges):
        self.shared_ranges = shared_ranges
        # self.x_ranges_set = False
        # self.shared_x_ranges = {}
        # if self.x_ranges_set is False:
        #     UserPlot.set_shared_x_ranges(
        #             parameters=parameters_dic
        #     )
        # self.all_y_columns = False
        self.legended = True
        self.plot_type = 'normal'
        self.utc_offset_hours = -4
        self.utc_offset_enabled = True
        self.max_points_plots = 500
        self.first_interval_hours = 24
        self.start_datetime_utc = None
        self.end_datetime_utc = None
        self.data_average_secs = None
        self.start_datetime_local = None
        self.end_datetime_local = None
        self.databases_ref = None
        self.width = 800
        self.height = 400
        self.webgl = False
        self.title = ''
        self.manual_last_time = False
        self.default_intervals = np.array(
                [1, 60, 3600, 24 * 3600, 24 * 3600 * 7,
                 24 * 3600 * 30, 24 * 3600 * 364]
        )
        self.min_border_left = 130
        self.toolbar_location = "right"

        for key in parameters_dic['plot_global_pars']:
            setattr(self,
                    key,
                    parameters_dic['plot_global_pars'][key])

        for key in dic:
            setattr(self, key, dic[key])

        self.set_start_end_datetime()

        self.set_data_average_secs()

        self.y_columns = {}
        self.legends = []
        self.name = name
        self.user_dic_pars = dic

        self.databases = {}

        for key in self.databases_ref:
            self.databases[key] = Database(
                    dic=parameters_dic['databases'][key],
                    user_plot=self
            )

        if self.name in self.shared_ranges.shared_x_ranges:
            self.x_range = self.shared_ranges.shared_x_ranges[self.name]
        else:
            self.x_range = Range1d()

        self.x_range.start = self.start_datetime_local
        self.x_range.end = self.end_datetime_local

        self.x_axis = DatetimeAxis(
                name='x_axis' + self.name,
                # x_range_name='x_range' + self.name
        )

        self.column_data_sources = dict()
        for key in self.databases_ref:
            self.column_data_sources[key] = self.databases[key].column_data_source

        self.plot = Plot(x_range=self.x_range,
                         y_range=Range1d(),
                         # x_axis_type="datetime",

                         min_border_left=self.min_border_left,
                         toolbar_location="right"

                         )
        self.plot.add_tools(PanTool(),
                            WheelZoomTool(),
                            ResizeTool(),
                            CrosshairTool(),
                            # PreviewSaveTool(),
                            # HoverTool()
                            )
        self.plot.add_layout(self.x_axis, 'below')

        self.plot.responsive = False

        self.plot.webgl = self.webgl

        self.plot.plot_width = self.width
        self.plot.plot_height = self.height

        # self.plot.extra_x_ranges['x_range' + self.name] = self.x_range

        self.plot.title = self.title

        # logger.debug('plot id is %s', self.plot._id)
        # logger.debug('y_column keys are %s', self.database.y_columns.keys())
        if self.plot_type is 'normal':
            self.setup_normal_plot()
        if self.plot_type is 'ceil':
            self.setup_ceil_plot()

    def setup_normal_plot(self):
        for database_key in self.databases_ref:
            database = self.databases[database_key]
            for col_name in database.y_columns.keys():
                # logger.debug('start y_colun loop %s', )
                col_dict = database.y_columns[col_name]
                self.y_columns[col_name] = UserYColumn(
                        name=col_name,
                        dic=col_dict,
                        user_plot=self,
                        x_range=self.x_range,
                        x_axis=self.x_axis,
                        plot=self.plot,
                        column_data_source=self.column_data_sources[database_key],
                        database=database
                )
                top = (
                    '{name} [{units}]'.format(
                            name=self.y_columns[col_name].show_name,
                            units=self.y_columns[col_name].units
                    )
                    ,
                    [self.y_columns[col_name].glyph_renderer, self.y_columns[col_name].glyph_renderer_circle]
                )
                self.legends.append(top)

        if self.legended:
            logger.debug('appending legend %s', self.name)
            self.plot.add_layout(
                    Legend(
                            legends=self.legends,
                            location='top_left',
                            # glyph_height=50,
                            # label_text_color=self.legend_text_colors
                            background_fill_alpha=0.8
                    )
            )

            # self.plot.add_layout(Legend(legends=[('a', [self.glyph_renderer])]))

    def setup_ceil_plot(self):

        self.plot.y_range.end = 250*15
        self.plot.y_range.start = 0
        self.plot.add_layout(LinearAxis(),'left')
        im = Image(
                x='x',
                y='y',
                image='image',
                dw='dw',
                dh='dh',
                color_mapper=LinearColorMapper(palette='Spectral11'),
                dilate=True
        )
        self.plot.add_glyph(self.column_data_sources[self.databases_ref[0]],im)




        # self.plot.add_layout(Legend(legends=[('a', [self.glyph_renderer])]))

    def update_y_ranges(self):
        for y_col in self.y_columns.itervalues():
            # logger.debug('updating %s', y_col)
            y_col.update_y_range()

    def set_data_average_secs(self):
        interval_secs = (self.end_datetime_utc - self.start_datetime_utc).total_seconds()
        raw_interval = interval_secs / self.max_points_plots
        rounding_int = find_nearest(self.default_intervals,
                                    raw_interval)
        self.data_average_secs = (
            round_base(raw_interval,
                       rounding_int)
        )
        self.data_average_secs = np.array([self.data_average_secs, 1]).max()

    def set_start_end_datetime(self):
        if self.manual_last_time is False:
            self.end_datetime_utc = datetime.datetime.utcnow()
        else:
            self.end_datetime_utc = datetime.datetime(*self.manual_last_time)
        self.start_datetime_utc = self.end_datetime_utc - datetime.timedelta(hours=self.first_interval_hours)
        self.set_local_from_utc()

    def set_local_from_utc(self):
        if self.utc_offset_enabled:
            self.start_datetime_local = self.start_datetime_utc + datetime.timedelta(hours=self.utc_offset_hours)
            self.end_datetime_local = self.end_datetime_utc + datetime.timedelta(hours=self.utc_offset_hours)
        else:
            self.start_datetime_local = self.start_datetime_utc
            self.end_datetime_local = self.end_datetime_utc

    def update(self):
        # logger.debug('starting update %s', self.name)
        x_range_type = type(self.x_range.end)
        logger.debug('xragne type is %s', x_range_type)
        if x_range_type is datetime.datetime:
            logger.debug('timezone is %s', timezone)
            # x_start = self.x_range.start.replace(tzinfo=timezone.utc).timestamp() * 1000
            # x_end = self.x_range.end.replace(tzinfo=timezone.utc).timestamp() * 1000
            x_start = (self.x_range.start.timestamp()) * 1000
            x_end = (self.x_range.end.timestamp()) * 1000

        else:
            x_end = self.x_range.end
            x_start = self.x_range.start
        # logger.debug('xrange type is %s for %s',
        #              type(self.x_range.end),
        #              self.name
        #              )
        end_datetime_candidate_local = (
            datetime.datetime.utcfromtimestamp(
                    x_end / 1000))
        start_datetime_candidate_local = (
            datetime.datetime.utcfromtimestamp(
                    x_start / 1000))

        if (
                    (
                                start_datetime_candidate_local !=
                                self.start_datetime_local
                    )
                and
                    (
                                end_datetime_candidate_local !=
                                self.end_datetime_local

                    )
        ):
            logger.debug('starting update of plot  %s', self.name)

            self.start_datetime_local = start_datetime_candidate_local
            self.end_datetime_local = end_datetime_candidate_local

            if self.utc_offset_enabled:
                current_offset_hours = self.utc_offset_hours
            else:
                current_offset_hours = 0

            self.end_datetime_utc = (
                self.end_datetime_local -
                datetime.timedelta(hours=current_offset_hours)
            )

            self.start_datetime_utc = (
                self.start_datetime_local -
                datetime.timedelta(hours=current_offset_hours)
            )

            self.set_data_average_secs()
            logger.debug('averagae secs is  %s',
                         self.data_average_secs)
            for database in self.databases.itervalues():
                database.set_column_data_source()
            self.update_y_ranges()

            # @classmethod
            # def set_shared_x_ranges(cls, parameters):
            #     if 'connected_plots' in parameters:
            #         for tups in parameters['connected_plots']:
            #             x_range = Range1d()
            #             for p_name in tups:
            #                 cls.shared_x_ranges[p_name] = x_range
            #         cls.x_ranges_set = True




class SharedRanges(object):
    def __init__(self, parameters):
        self.shared_x_ranges = {}
        if 'connected_plots' in parameters:
            for tups in parameters['connected_plots']:
                x_range = Range1d()
                for p_name in tups:
                    self.shared_x_ranges[p_name] = x_range
        logger.debug('connected ranges are %s', self.shared_x_ranges)
        self.x_ranges_set = True


def round_base(x, base=5):
    return int(base * round(float(x) / base))


def find_nearest(array, value):
    idx = (np.abs(array - value)).argmin()
    return array[idx]
