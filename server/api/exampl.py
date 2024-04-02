'''
INTERACTIVIDAD CON SLIDERS EN BOKEH

Ignacio Díaz Blanco, 2020. Universidad de Oviedo
'''

import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file

from bokeh.io import show, curdoc
from bokeh.models import Div, ColumnDataSource, Slider, CustomJS
from bokeh.layouts import layout, Column



# DATOS INICIALES
N = 1000
t = np.linspace(0,100,N)
x = np.sin(t)
y = np.sin(2*t)
z = np.sin(3*t)


# SOURCE: FUENTE COMÚN DE DATOS
# el source puede verse como una tabla 
# en este caso, tiene N muestras y atributos 'x', 'y', 'z'
datos = {
	't': t,
	'x': x,
	'y': y,
	'z':z
}

# generamos el objeto "source"
source = ColumnDataSource(datos)

# este objeto es una "fuente de datos" común
# que "sincroniza" todas las figuras
# cualquier cambio en los datos (modificación, selección)
# es inmediatamente actualizado por Boheh en 
# todas las figuras que tengan esa fuente





# ELEMENTOS INTERACTIVOS
# SLIDERS y su función callback
slider1 = Slider(start=-5, end=5, value=0, step=.01, title="a")
slider2 = Slider(start=-5, end=5, value=1, step=.01, title="b")
slider3 = Slider(start=-5, end=5, value=0, step=.01, title="c")

def callback(attr,old,new):
    a = slider1.value
    b = slider2.value
    c = slider3.value
    print(a)
    source.data['x'] = np.sin(t + a)
    source.data['y'] = b*np.sin(2*t)
    source.data['z'] = np.sin(3*t + c)


slider1.on_change('value',callback)
slider2.on_change('value',callback)
slider3.on_change('value',callback)






# FIGURA
# creamos la figura
f1 = figure(width=400,height=400,tools="crosshair,box_select,pan,reset,wheel_zoom",y_range=(-2,2),x_range=(-2,2))
p1 = f1.line(x='x', y='y', source=source,line_width=2,line_alpha=0.5,legend_label='y(t)')

f2 = figure(width=400,height=400,tools="crosshair,box_select,pan,reset,wheel_zoom",y_range=(-2,2),x_range=(-2,2))
p2 = f2.line(x='y', y='z', source=source,line_width=2,line_alpha=0.5,legend_label='z(t)')




# ELEMENTO DE TEXTO
div = Div(text='''
<h1>Interactividad en Bokeh con callbacks de Python</h1>
<h2>(bokeh server)</h2>
<i>Ignacio Díaz Blanco, 2021. Universidad de Oviedo</i>
<table cellpadding=5>
<td valign="top">
<p>En este ejemplo se utilizan widgets de tipo <i>slider</i>. Cuando cualquiera de los sliders cambia, se ejecuta una <i>callback</i> en python. Las callbacks de python dan más flexibilidad pues permiten el uso de librerías de python (ej. <code>sklearn</code>), pero en requieren el uso de un servidor (<code>bokeh server</code>)</p>
</td>
<td valign="top">
<p>La callback modifica los datos de <code>source</code>, resultando en una actualización "inmediata" y en tiempo real de las gráficas</p></td>
</table>
Para ejecutarlo hacer: <br />
<code>
bokeh serve nombre_del_script.py --show
</code> 
<br></br>
<a href="fuentes/%s">(código fuente)</a>'''%(__file__.split('.')[0]+'_codigofuente.html'),width=700)


divhueca = Div(height=150)




# ORGANIZACIÓN DE LOS COMPONENTES: FIGURA, TEXTO
lay = layout([
	[div,[divhueca,slider1,slider2,slider3]],
	[f1,f2],
	
	])


curdoc().add_root(lay)
curdoc().title = "Ejemplo interactividad sliders (servidor)"