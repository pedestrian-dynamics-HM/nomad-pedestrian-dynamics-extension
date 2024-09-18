from nomad_pedestrian_dynamics_extension.vadere_parser.parser import VadereParser

from pydantic import Field
from nomad.config.models.plugins import ParserEntryPoint


class VadereParserEntryPoint(ParserEntryPoint):

    def load(self):
        print("Load Vadere parser")
        from nomad_pedestrian_dynamics_extension.vadere_parser.parser import VadereParser
        return VadereParser(**self.dict())


vadere_parser = VadereParserEntryPoint(
    name = 'parser/vadere',
    description = 'Vadere parser.',
    mainfile_name_re = 'postvis.traj',
)
