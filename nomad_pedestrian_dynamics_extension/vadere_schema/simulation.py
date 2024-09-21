#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from typing import TYPE_CHECKING

from nomad_pedestrian_dynamics_extension.vadere_schema.model import Model
from nomad_pedestrian_dynamics_extension.vadere_schema.scenario import Scenario

if TYPE_CHECKING:
    pass


import numpy as np
from nomad.datamodel.data import Schema
from nomad.metainfo import Datetime, Quantity, SchemaPackage, SubSection



m_package = SchemaPackage()

class Simulation(Schema):

    software_name = Quantity(
        type=str, description="""Name of the software used for the simulation."""
    )

    software_release = Quantity(type=str, description="""Software release.""")

    date = Quantity(type=Datetime, description="""Start time of the execution.""")

    model = SubSection(sub_section=Model, description="""Simulation model.""")

    seed = Quantity(type = np.int64, description="""Simulation seed""",
    )

    total_simulation_time = Quantity(
        type = np.float64,
        description="""Total simulation time""",
    )

    scenario = SubSection(sub_section=Scenario,
                          description="""Scenario properties."""
                          )


m_package.__init_metainfo__()
