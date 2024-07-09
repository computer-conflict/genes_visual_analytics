# Bokeh imports
from bokeh.models import ColumnDataSource, CategoricalColorMapper
from bokeh.plotting import figure
from bokeh.palettes import d3

# Utils imports
from typing import List
import pandas as pd
import os

class PlotsHelper:
    @staticmethod
    def _get_color_map():
        # Obtain example dataset
        directory_path = f"./db/datasets/modified_datasets"
        datasets = os.listdir(directory_path)

        csv_datasets = [file for file in datasets if file.endswith(".csv")]
        if not csv_datasets:
          raise FileNotFoundError("No se encontraron archivos CSV en el directorio de datasets modificados.")

        first_csv_file = csv_datasets[0]
        path = os.path.join(directory_path, first_csv_file)
        df = pd.read_csv(path)

        # Get palette from dataset catergories
        categories = list(map( lambda x: str(x), df['cluster'].unique()))
        palette = d3['Category20'][12] #len(categories)
        return CategoricalColorMapper(factors=categories, palette=palette)

    @staticmethod
    def _get_plots_tooltip() -> str:
        tooltip = """
          <div
            class="figure-tootip"
            style="overflow: none; width: 300px"
          >
            <p><strong>Nombre:</strong>@{symbol}</p>
            <strong>Descripción</strong>
            <p>@{summary}</p>
          </div>
        """

        return tooltip

    #
    # Returns a list of figures that shares a ColumnDataSource.
    # @Returns
    #
    @staticmethod
    def get_plots(source: ColumnDataSource) -> List[figure]:
        """
        Retorna un array de objetos :class:`figure` que comparten la misma fuente de datos.

        La fuente que las figuras comparten es un :class:`ColumnDataSource`.

        Parámetros
        ----------
        source : ColumnDataSource
            La fuente de datos que se compartirá entre las figuras.

        Retorna
        -------
        plots : List[figure]
            Array de :class:`figure`.

        Este método crea y retorna una lista de figuras de Bokeh que utilizan la misma fuente de datos,
        permitiendo así la sincronización de datos entre ellos.
        """

        TOOLTIPS = PlotsHelper._get_plots_tooltip()
        color_map = PlotsHelper._get_color_map()

        #  -- Plots figures & callbacks
        summaries_plot = figure(tooltips=TOOLTIPS,
                                match_aspect=True,
                                tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select",
                                title='Representación semántica de los genes',
                                sizing_mode='scale_width')
        summaries_plot.scatter(x='summary_x', y='summary_y', source=source, marker="circle",
                               radius=0.02, selection_color="red", nonselection_fill_alpha=0.01,
                               color='summary_color')

        set_1_plot = figure(name='expresions_plot', match_aspect=True,
            tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select",
            title='Representación de las expresiones genéticas', tooltips=TOOLTIPS)
        set_1_plot.scatter(x='set_1_x', y='set_1_y', source=source, marker="circle",
                            radius=0.02, selection_color="red",  nonselection_fill_alpha=0.01,
                            color='set_1_color')

        set_2_plot = figure(name='expresions_plot', match_aspect=True,
            tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select",
            title='Representación de las expresiones genéticas', tooltips=TOOLTIPS)
        set_2_plot.scatter(x='set_2_x', y='set_2_y', source=source, marker="circle",
                            radius=0.02, selection_color="red",  nonselection_fill_alpha=0.01,
                            color='set_2_color')

        return [summaries_plot, set_1_plot, set_2_plot]


