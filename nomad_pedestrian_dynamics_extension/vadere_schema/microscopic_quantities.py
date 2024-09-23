from ase.visualize.mlab import description
from nomad.datamodel import ArchiveSection
from nomad.metainfo import Section, SubSection

from nomad_pedestrian_dynamics_extension.vadere_schema.trajectories import Trajectories


class MicroscopicResults(ArchiveSection):

    m_def = Section(description= "This section contains the trajectory of each (virtual) pedestrian.")

    trajectories = SubSection(
        sub_section=Trajectories.m_def,
        repeats=True,
        description = "Position in the x-y-plane over time."
    )
