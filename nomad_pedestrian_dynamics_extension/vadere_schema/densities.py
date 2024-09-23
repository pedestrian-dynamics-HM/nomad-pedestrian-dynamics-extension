import numpy as np
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
from nomad.metainfo import Section, Quantity
from plotly import graph_objs as go


class Densities(PlotSection):

    m_def = Section()

    time = Quantity(
        type=np.float64,
        description="""Simulation time""",
        unit="s"
    )

    densities = Quantity(
        type=np.float64,
        shape=['1...*', '1...*'],
        description="""Pedestrian density""",
        unit="1/m**2"
    )

    max_density = Quantity(
        type = np.float64,
        unit="1/m**2",
        description="""Maximum pedestrian density""",
    )


    def normalize(self, archive, logger):

        super(Densities, self).normalize(archive, logger)
        densities_plot = np.flip(self.densities.transpose(),0)
        heatmap = go.Heatmap(z=densities_plot, zmin=0, zmax=self.max_density, showscale=True, colorbar=dict(thickness=5,title="Pedestrian density"))
        figure1 = go.Figure(data=heatmap, layout=dict(yaxis=dict(scaleanchor='x', scaleratio=1.0)))
        figure_json = figure1.to_plotly_json()
        self.figures.append(PlotlyFigure(label='Density', index=0, figure=figure_json))
