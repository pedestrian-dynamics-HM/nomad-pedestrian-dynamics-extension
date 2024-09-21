from nomad.datamodel import ArchiveSection
from nomad.metainfo import Section, SubSection

from nomad_pedestrian_dynamics_extension.vadere_schema.trajectories import Trajectories


class MicroscopicResults(ArchiveSection):


    m_def = Section()

    trajectories = SubSection(
        sub_section=Trajectories.m_def,
        repeats=True
    )
