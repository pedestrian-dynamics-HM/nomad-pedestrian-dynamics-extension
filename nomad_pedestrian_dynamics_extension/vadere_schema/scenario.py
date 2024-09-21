import numpy as np
from nomad.datamodel import ArchiveSection
from nomad.metainfo import Section, Quantity


class Scenario(ArchiveSection):

    m_def = Section()

    number_of_sources = Quantity(
        type = np.int64, description="""Number of sources where agents are spawned."""
    )

    number_of_targets = Quantity(
        type=np.int64, description="""Number of targets."""
    )

    dimensions = Quantity(
        type=np.float64,
        shape=[2] ,
        description="""Outer dimension of the topography (width x height).""",
        unit='m'
    )

    #TODO: implement
    origin_destination_matrix = Quantity(
        type=np.float64, shape=['number_of_sources', 'number_of_targets'], description="""Origin destination matrix."""
    )
