import numpy as np
from nomad.datamodel.results import Properties
from nomad.metainfo import Section, Quantity


class ScenarioProperties(Properties):

    m_def = Section()

    total_number_of_pedestrians = Quantity(
        type=np.int64,
        description="""Total number of pedestrians in the simulation""",
        default=0
    )

    max_number_of_pedestrians = Quantity(
        type=np.int64,
        description="""Maximum number of pedestrians in the simulation. Corresponds the total number in case of a one time spawning""",
        default=0
    )
