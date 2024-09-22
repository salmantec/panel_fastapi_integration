import fastapi
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import panel as pn
import numpy as np
from bokeh.plotting import figure
import threading

PANEL_PORT = 5123

plot_app = FastAPI()

def create_app():
    pn.extension("bokeh")
    pn.extension("tabulator")

    return create_panel().servable()


def create_panel():
    # Sample data
    x = np.linspace(0, 10, 100)
    data = {
        'Sine': np.sin(x),
        'Cosine': np.cos(x),
        'Tangent': np.tan(x)
    }

    # Define Panel components
    checkbox_group = pn.widgets.CheckBoxGroup(name='Select Functions', options=list(data.keys()), inline=True)
    radio_button = pn.widgets.RadioButtonGroup(name='Select Line Style', options=['Solid', 'Dashed', 'Dotted'], button_type='success')

    # Function to create a Bokeh plot
    def create_plot(selected_functions, line_style):
        plot = figure(title="Line Graph", x_axis_label='X-axis', y_axis_label='Y-axis')
        
        for function in selected_functions:
            y = data[function]
            line_type = {'Solid': 'solid', 'Dashed': 'dashed', 'Dotted': 'dotted'}[line_style]
            plot.line(x, y, line_width=2, line_dash=line_type, legend_label=function)
        
        plot.legend.location = "top_left"
        # plot.grid
        return plot

    sidebar = pn.Column(
        checkbox_group,
        radio_button
    )

    switch_sidebar = pn.widgets.Switch(name="Config - Sidebar", value=True)

    # Bind the plot to the selected values of the widgets
    plot_pane = pn.pane.Bokeh(
        create_plot([], 'Solid'),  # Initial empty plot
        height=700
    )

    def update_plot(*events):
        selected_functions = checkbox_group.value
        line_style = radio_button.value
        plot_pane.object = create_plot(selected_functions, line_style)

    checkbox_group.param.watch(update_plot, 'value')
    radio_button.param.watch(update_plot, 'value')

    main_content = pn.Column(
        # pn.Row(create_plot, height=700, sizing_mode="stretch_both", width_policy="max", height_policy="max"),
        plot_pane
    )
    
    main = pn.Row(sidebar, main_content, sizing_mode="stretch_both")

    def switch_sidebar_event(switch_event):
        main[0].visible = switch_event.new

    switch_sidebar.param.watch(switch_sidebar_event, "value")

    return pn.Column(switch_sidebar, main, sizing_mode="stretch_both")



def _create_server():
    try:
        pn.serve(
            {"/app": create_app},
            allow_websocket_origin=["*"],
            address="0.0.0.0",
            port=PANEL_PORT,
            show=False,
            threaded=False,
        )
    except OSError:
        pass
    else:
        return

def create_server():
    threading.Thread(target=_create_server, daemon=True).start()


create_server()

@plot_app.get("/plot")
async def plot_page(request: Request):
    try:
        script = server_document(f"http://{request.url.hostname}:{PANEL_PORT}/app")
        return templates.TemplateResponse(request, "plot_app.html", {"script": script})
    except Exception:
        pass
