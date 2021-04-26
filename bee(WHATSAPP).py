import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

#import
df = pd.read_csv("bees.csv")
df = df[df['Year'] == 2015]

# ID COLUMN
df['id'] = df['state_code']
df.set_index('id', inplace=True, drop=False)
print(df.columns)


# Application layout
app = dash.Dash(__name__, prevent_initial_callbacks=True)


app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
            if i == "code" or i == "Year" or i == "id"
            else {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="single",
        column_selectable="multi",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=6,
        style_cell={
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['State', 'code']
        ],
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),

    html.Br(),
    html.Br(),
    html.Div(id='bar-container'),
    html.Div(id='choromap-container')

])


# -------------------------------------------------------------------------------------
# Create bar chart
@app.callback(
    Output(component_id='bar-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
     Input(component_id='datatable-interactivity', component_property='selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
     Input(component_id='datatable-interactivity', component_property='active_cell'),
     Input(component_id='datatable-interactivity', component_property='selected_cells')]
)
def update_bar(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows,
               order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):
    print('***************************************************************************')
    print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    print('---------------------------------------------')
    print("Indices of selected rows if part of table after filtering:{}".format(slctd_row_indices))
    print("Names of selected rows if part of table after filtering: {}".format(slct_rows_names))
    print("Indices of selected rows regardless of filtering results: {}".format(slctd_rows))
    print('---------------------------------------------')
    print("Indices of all rows pre or post filtering: {}".format(order_of_rows_indices))
    print("Names of all rows pre or post filtering: {}".format(order_of_rows_names))
    print("---------------------------------------------")
    print("Complete data of active cell: {}".format(actv_cell))
    print("Complete data of all selected cells: {}".format(slctd_cell))

    dff = pd.DataFrame(all_rows_data)

    # used to highlight selected countries on bar chart
    colors = ['#7FDBFF' if i in slctd_row_indices else '#0074D9'
              for i in range(len(dff))]

    if "State" in dff and "affected" in dff:
        return [
            dcc.Graph(id='bar-chart',
                      figure=px.bar(
                          data_frame=dff,
                          x="State",
                          y='colonies',
                          labels={"affected": "bees colonies"}
                      ).update_layout(showlegend=False, xaxis={'categoryorder': 'total ascending'})
                      .update_traces(marker_color=colors, hovertemplate="<b>%{y}%</b><extra></extra>")
                      )
        ]


# -------------------------------------------------------------------------------------
# Create choropleth map
@app.callback(
    Output(component_id='choromap-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows')]
)
def update_map(all_rows_data, slctd_row_indices):
    dff = pd.DataFrame(all_rows_data)

    # highlight selected countries on map
    borders = [5 if i in slctd_row_indices else 1
               for i in range(len(dff))]

    if "code" in dff and "colonies" in dff and "State" in dff:
        return [
            dcc.Graph(id='choropleth',
                      style={'height': 700},
                      figure=px.choropleth(
                          data_frame=dff,
                          locations="code",
                          locationmode='USA-states',
                          scope="usa",
                          color="colonies",
                          color_continuous_scale=px.colors.sequential.YlOrRd,

                          title="colonies affected",
                          template='plotly_dark',
                          hover_data=['State', 'colonies','code'],
                      ).update_layout(showlegend=False, title=dict(font=dict(size=28), x=0.5, xanchor='center'))
                      .update_traces(marker_line_width=borders, hovertemplate="<b>%{customdata[0]}</b><br><br>" +
                                                                              "%{customdata[1]}" + "%")
                      )
        ]


# -------------------------------------------------------------------------------------
# Highlight selected column
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# -------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run_server(debug=True)