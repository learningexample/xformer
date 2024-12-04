from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define common card style
CARD_STYLE = {"height": "200px", "textAlign": "center"}

# Helper function to create a card
def create_card(title, content):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                html.P(content, className="card-text"),
            ]
        ),
        style=CARD_STYLE,
    )

app.layout = dbc.Container(
    dbc.Row(
        [
            dbc.Col(create_card("Card 1", "Content of the first card."), xs=12, sm=6, md=4, lg=3),
            dbc.Col(create_card("Card 2", "Content of the second card."), xs=12, sm=6, md=4, lg=3),
            dbc.Col(create_card("Card 3", "Content of the third card."), xs=12, sm=6, md=4, lg=3),
            dbc.Col(create_card("Card 4", "Content of the fourth card."), xs=12, sm=6, md=4, lg=3),
        ]
    ),
    fluid=True,
)

if __name__ == "__main__":
    app.run_server(debug=True)
