import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import requests
import json

def create_circles(service_response):
    x_values = service_response['x']
    y_values = service_response['y']
    radii = service_response['radii']
    return [
        dict(
            type="circle",
            xref="x",
            yref="y",
            x0=x_values[i] - radii[i],
            y0=y_values[i] - radii[i],
            x1=x_values[i] + radii[i],
            y1=y_values[i] + radii[i],
        ) for i in range(len(x_values))
    ]

def create_figure(service_response):
    fig = go.Figure()

    # Add circles
    fig.update_layout(
        shapes=create_circles(service_response)
    )

    fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))

    return fig


app = dash.Dash(__name__)
id_column = {
    "name": "ID",
    "id": "column-id",
    "deletable": False,
    "renamable": False,
    "editable": False,
}
diameter_column = {
    "name": "Diameter",
    "id": "column-dia",
    "deletable": False,
    "renamable": False,
    "editable": True,
}
count_column = {
    "name": "Count",
    "id": "column-count",
    "deletable": False,
    "renamable": False,
    "editable": True,
}
ROW_ID = 1
app.layout = html.Div([
    dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")], type="default"),
    html.Div([
        html.Button("Add Row", id="editing-rows-button", n_clicks=0),
        html.Button("Solve", id="solve-input-button", n_clicks=0),
   ]),
    html.Div(
        [
            dash_table.DataTable(
                id="adding-rows-table",
                columns=[id_column, diameter_column, count_column],
                data=[],
                editable=False,
                row_deletable=True,
                style_table={
                    'maxHeight': '50ex',
                    'overflowY': 'scroll',
                    'width': '100%',
                    'minWidth': '100%',
                },
            ),
        ],
        style={'width': '50%', 'display': 'inline-block'}
    ),
   html.Div(
        [
            dcc.Graph(id="adding-rows-graph"),
        ],
        style={'width': '50%', 'display': 'inline-block'}
   ),
])


@app.callback(
    Output("adding-rows-table", "data"),
    [Input("editing-rows-button", "n_clicks")],
    [State("adding-rows-table", "data"), State("adding-rows-table", "columns")],
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        global ROW_ID
        new_row = {c["id"]: "" for c in columns}
        new_row["column-id"] = f"{ROW_ID}"
        ROW_ID += 1
        rows.append(new_row)
    return rows


@app.callback(
    [Output("adding-rows-graph", "figure"), Output("loading-output-1", "children")],
    [Input("solve-input-button", "n_clicks")],
    [State("adding-rows-table", "data"), State("adding-rows-table", "columns")],
)
def solve_table(n_clicks, rows, columns):
    if n_clicks > 0:
        diameters = [float(row['column-dia']) for row in rows]
        count = [int(row['column-count']) for row in rows]

        resp = requests.post("http://127.0.0.1:5002/solves/solve_configuration", data=json.dumps({'diameters': diameters, 'count': count}))


        return create_figure(json.loads(resp.text)), False

    else:
        return dash.no_update


if __name__ == "__main__":
    app.run_server(debug=True)
