import numpy as np
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
from nomad.metainfo import Section, Quantity
from plotly import express as px



class Trajectories(PlotSection):

    m_def = Section()


    pedestrian_id = Quantity(
        type=np.int64,
        description="""Pedestrian id""",
    )

    time = Quantity(
        type=np.float64,
        shape=['1...*'],
        description="""Point of time""",
    )

    position_x = Quantity(
        type=np.float64,
        shape=['1...*'],
        description="""X-Position""",
    )

    position_y = Quantity(
        type=np.float64,
        shape=['1...*'],
        description="""Y-Position""",
    )


    def normalize(self, archive, logger):

        super(Trajectories, self).normalize(archive, logger)

        figure1 = px.scatter(x=self.position_x, y=self.position_y, title=f"X-Y-Position - pedestrian id = {self.pedestrian_id}")
        figure1.layout.yaxis.scaleanchor = "x"
        figure_json = figure1.to_plotly_json()
        self.figures.append(PlotlyFigure(label='X-Y-Position', index=0, figure=figure_json))
