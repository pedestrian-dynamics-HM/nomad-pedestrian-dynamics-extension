
from pydantic import Field
from typing import Optional

from nomad.config.models.plugins import ParserEntryPoint

class EntryPoint(ParserEntryPoint):
    parser_class_name: str = Field(
        description="""
        The fully qualified name of the Python class that implements the parser.
        This class must have a function `def parse(self, mainfile, archive, logger)`.
    """
    )
    code_name: Optional[str]
    code_homepage: Optional[str]
    code_category: Optional[str]
    metadata: Optional[dict] = Field(
        description="""
        Metadata passed to the UI. Deprecated. """
    )

    def load(self):
        from nomad.parsing import MatchingParserInterface

        return MatchingParserInterface(**self.dict())


vadere_parser_entry_point = EntryPoint(
    name='parsers/vadere',
    aliases=['parsers/vadere'],
    description='NOMAD parser for Vadere.',
    python_package='nomad_pedestrian_dynamics_extension.vadere_parser',
    mainfile_name_re=r'^.*\postvis.traj',
    parser_class_name='nomad_pedestrian_dynamics_extension.vadere_parser.VadereParser', #TODO check if parser is missing in path
    code_name='Vadere',
    code_homepage='https://vadere.org/',
    code_category='Pedestrian dynamics code',
    metadata={
        'codeCategory': 'Pedestrian dynamics code',
        'codeLabel': 'Vadere',
        'codeLabelStyle': 'only first character in capitals',
        'codeName': 'Vadere',
        'codeUrl': 'https://vadere.org/',
        'parserGitUrl': '',
        'parserSpecific': '',
        'status': '',
        'tableOfFiles': '',
    },
)