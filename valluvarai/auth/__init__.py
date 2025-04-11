"""
Authentication module for ValluvarAI.
"""

from valluvarai.auth.auth_manager import AuthManager
from valluvarai.auth.models import User, UserPreferences

# Create a global auth manager instance
auth_manager = AuthManager()
