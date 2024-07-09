# Bokeh imports
from bokeh.models import ColumnDataSource, Toggle
from bokeh.plotting import figure
from bokeh.events import MouseMove

# Import utils
from typing import List
from functools import partial
import time

class ToolsHelper:
    @staticmethod
    def filter_points_near_point(x_ref, y_ref, x_list, y_list, max_distance):
        index_list = []
        for i, (x, y) in enumerate(zip(x_list, y_list)):
            distance = ((x - x_ref)**2 + (y - y_ref)**2)**0.5
            if distance < max_distance:
                index_list.append(i)

        return index_list

    @staticmethod
    def attach_brusshing_to_plots(source: ColumnDataSource, summaries_plot: figure, set_1_plot: figure, set_2_plot: figure, brusshing_tool: Toggle) -> List[figure]:
        """
        Habilita la herramienta de brushing en una serie de figuras de Bokeh y asocia un Toggle como disparador.

        Args:
            source :ColumnDataSource: La fuente de datos que se compartirá entre las figuras.
            summaries_plot :figure: Primera figura a la que se añadirá la herramienta de brushing.
            set_1_plot :figure: Segunda figura a la que se añadirá la herramienta de brushing.
            set_2_plot :figure: Tercera figura a la que se añadirá la herramienta de brushing.
            brushing_tool :Toggle: El Toggle que actúa como disparador para la herramienta de brushing.

        Returns:
            List[figure]: Una lista de figuras con la herramienta de brushing habilitada.

        Este método recibe tres figuras de Bokeh y un Toggle. Habilita la herramienta de brushing en
        cada una de las figuras, permitiendo la selección y el resaltado sincronizado de datos en
        todas las figuras. El Toggle actúa como un disparador que controla el estado de la herramienta
        de brushing.
        """

        def brushing(e, plot_name):
            '''
            Definicion de la herramienta de brushing.
            '''
            if not brusshing_tool.active: return

            x = e.x
            y = e.y

            x_list = source.data[f"{plot_name}_x"]
            y_list = source.data[f"{plot_name}_y"]

            start_time = time.time()
            index = ToolsHelper.filter_points_near_point(x, y, x_list, y_list, 0.33)
            end_time = time.time()
            source.selected.indices = index
            print("")
            print(f"Brushing  time: {end_time - start_time} s")

        summaries_plot.on_event(MouseMove, partial(brushing, plot_name='summary'))
        set_1_plot.on_event(MouseMove, partial(brushing, plot_name='set_1'))
        set_2_plot.on_event(MouseMove, partial(brushing, plot_name='set_2'))

        return [summaries_plot, set_1_plot, set_2_plot]