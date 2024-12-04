from dash import Dash, html
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Mock card data
CARDS = [
    {
        "title": "Portfolio Management",
        "description": "Manage your portfolios effectively with advanced tools and insights.",
        "link_text": "Learn More",
        "link_url": "#",
    },
    {
        "title": "Market Insights",
        "description": "Get the latest market trends, analysis, and expert opinions to stay ahead.",
        "link_text": "Explore",
        "link_url": "#",
    },
    {
        "title": "Investment Tools",
        "description": "Access a range of powerful tools to support your investment decisions.",
        "link_text": "Try Tools",
        "link_url": "#",
    },
    {
        "title": "Client Reporting",
        "description": "Generate detailed, professional client reports effortlessly.",
        "link_text": "Start Reporting",
        "link_url": "#",
    },
]

# Generate card components
cards = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.H5(card["title"], className="card-title text-dark"),
                        className="bg-light text-center",
                        style={"borderBottom": "1px solid silver"},
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                card["description"],
                                className="card-text text-muted",
                                style={
                                    "overflow": "hidden",
                                    "textOverflow": "ellipsis",
                                    "display": "-webkit-box",
                                    "-webkit-line-clamp": 3,
                                    "-webkit-box-orient": "vertical",
                                },
                            ),
                            html.A(
                                card["link_text"],
                                href=card["link_url"],
                                className="btn btn-primary mt-auto",
                                style={"backgroundColor": "#1E90FF", "border": "none"},
                            ),
                        ],
                        style={"display": "flex", "flexDirection": "column", "height": "100%"},
                    ),
                ],
                className="mb-4 shadow-sm hover-card",
                style={
                    "height": "20rem",
                    "display": "flex",
                    "flexDirection": "column",
                    "border": "1px solid silver",
                    "borderRadius": "10px",
                    "transition": "transform 0.2s, box-shadow 0.2s",
                },
            ),
            xs=12, sm=6, md=4, lg=3,
        )
        for card in CARDS
    ],
    className="g-3",
)

# App layout
app.layout = dbc.Container(
    [
        dbc.Navbar(
            dbc.Container(
                [
                    dbc.NavbarBrand("Investment Management Portal", className="ms-2 text-dark fw-bold"),
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink("Log Out", href="#", className="text-dark")),
                            dbc.NavItem(dbc.NavLink("Feedback", href="#", className="text-dark")),
                            dbc.NavItem(dbc.NavLink("Help", href="#", className="text-dark")),
                        ],
                        className="ms-auto",
                    ),
                ]
            ),
            style={"backgroundColor": "#F8F9FA", "borderBottom": "1px solid silver"},
            className="mb-4 shadow-sm",
        ),
        cards,
        html.Div(
            [
                html.P("© 2024 Investment Advisors Inc. All rights reserved.", className="mb-2 text-muted"),
                html.A("Privacy Policy", href="#", className="me-3 text-muted"),
                html.A("Terms of Service", href="#", className="text-muted"),
            ],
            className="text-center mt-4",
        ),
    ],
    fluid=True,
    style={"backgroundColor": "#F8F9FA", "paddingBottom": "20px"},
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
