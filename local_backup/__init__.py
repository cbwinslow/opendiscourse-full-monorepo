"""
OpenDiscourse - A platform for tracking and analyzing political discourse
"""
__version__ = "0.1.0"

# Import key classes and functions for easy access
from .openstates_api import OpenStatesAPI, create_openstates_client
from .congress_gov_api import CongressGovAPI, ProPublicaCongressAPI, create_congress_gov_client, create_propublica_client
from .openlegislation_api import OpenLegislationAPI, create_openlegislation_client
from .govinfo_api import GovInfoAPI, create_govinfo_client
from .unified_api import UnifiedAPISuite, create_unified_api_suite

# Define what gets imported with "from opendiscourse import *"
__all__ = [
    'OpenStatesAPI',
    'CongressGovAPI',
    'ProPublicaCongressAPI',
    'OpenLegislationAPI',
    'GovInfoAPI',
    'UnifiedAPISuite',
    'create_openstates_client',
    'create_congress_gov_client',
    'create_propublica_client',
    'create_openlegislation_client',
    'create_govinfo_client',
    'create_unified_api_suite'
]