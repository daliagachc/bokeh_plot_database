# project name: pyranometer
# created by diego aliaga daliaga_at_chacaltaya.edu.bo
from bokeh.models import Range1d, DataRange1d, LinearAxis, Line, Circle
import my_logger

logger = my_logger.get_logger(name=__name__, level='DEBUG')


class UserYColumn(object):
    name = None
    units = ''
    glyph = None
    glyph_renderer = None
    glyph_renderer_circle = None
    y_axis = None
    x_axis = None
    y_range = None
    x_range = None
    user_plot = None
    column_data_source = None
    database = None
    max_value = 1
    min_value = 0
    color = 'black'
    plot_name = None

    def __init__(self, name, dic, user_plot,
                 x_range, x_axis, plot,
                 column_data_source, database
                 ):
        self.name = name
        self.plot_name = user_plot.name
        self.dic = dic
        self.user_plot = user_plot
        for key in dic:
            setattr(self, key, dic[key])
        self.x_range = x_range
        self.x_axis = x_axis
        self.y_range = DataRange1d(range_padding=0.05,
                                   name=self.plot_name + self.name,
                                   default_span=1
                                   )
        self.plot = plot
        self.column_data_source = column_data_source
        self.database = database

        self.y_axis = LinearAxis(
                y_range_name=self.plot_name + self.name,
                major_label_text_color=self.color,
                axis_line_color=self.color,
                major_tick_line_color=self.color,
                minor_tick_line_color=self.color,
                # name=name

        )

        self.plot.extra_y_ranges[self.plot_name + self.name] = self.y_range
        self.plot.add_layout(self.y_axis, 'left')

        self.glyph = Line(y=self.name,
                          x=self.database.time_column_name,
                          line_color=self.color
                          )

        self.glyph_circle = Circle(y=self.name,
                                   x=self.database.time_column_name,
                                   fill_color=self.color,
                                   line_alpha=0
                                   )

        self.glyph_renderer_circle = plot.add_glyph(

                self.column_data_source,
                self.glyph_circle,
                y_range_name=self.plot_name + self.name,
                x_range_name='x_range' + self.plot_name
        )

        self.glyph_renderer = plot.add_glyph(

                self.column_data_source,
                self.glyph,
                y_range_name=self.plot_name + self.name,
                x_range_name='x_range' + self.plot_name
        )

        self.y_range.renderers = [self.glyph_renderer]

        logger.debug('plot id is %s', self.plot._id)

    def update_y_range(self):

        start = self.database.min_dataframe[self.name]
        end = self.database.max_dataframe[self.name]
        interval = end - start
        logger.debug('interval is %s', interval)
        if interval <= 0:
            interval = 1
        self.y_range.start = (
            start - interval * .05
        )
        self.y_range.end = (
            end + interval * .05
        )

        logger.debug('yrange start is %s', self.y_range.start)
        logger.debug('yrange end is %s', self.y_range.end)
