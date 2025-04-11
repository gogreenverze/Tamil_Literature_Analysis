"""
Authentication manager for ValluvarAI.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

try:
    import jwt
    from passlib.context import CryptContext
    AUTH_LIBS_AVAILABLE = True
except ImportError:
    AUTH_LIBS_AVAILABLE = False
    print("Authentication libraries not available. Please install them with:")
    print("pip install python-jose[cryptography] passlib[bcrypt] pydantic[email]")

from valluvarai.auth.models import User, UserInDB, UserCreate, UserUpdate, Token, TokenData, UserPreferences
from valluvarai.config import config


class AuthManager:
    """Authentication manager for ValluvarAI."""
    
    def __init__(self, users_file: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize the authentication manager.
        
        Args:
            users_file: Path to the users JSON file. If None, uses the default path.
            secret_key: Secret key for JWT token generation. If None, uses the default from config.
        """
        # Check if authentication libraries are available
        if not AUTH_LIBS_AVAILABLE:
            self.enabled = False
            return
        
        self.enabled = True
        
        # Set up password context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Set up JWT settings
        self.secret_key = secret_key or os.environ.get("JWT_SECRET_KEY") or "valluvarai_secret_key"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # Set up users file
        if users_file:
            self.users_file = Path(users_file)
        else:
            self.users_file = Path.home() / ".valluvarai" / "users.json"
        
        # Create users file directory if it doesn't exist
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load users from file
        self.users = self._load_users()
        
        # Create admin user if no users exist
        if not self.users:
            self._create_admin_user()
    
    def _load_users(self) -> Dict[str, UserInDB]:
        """
        Load users from file.
        
        Returns:
            Dictionary of users.
        """
        if not self.users_file.exists():
            return {}
        
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                users_data = json.load(f)
                
                # Convert JSON data to UserInDB objects
                users = {}
                for username, user_data in users_data.items():
                    # Convert datetime strings to datetime objects
                    if "created_at" in user_data and isinstance(user_data["created_at"], str):
                        user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                    if "last_login" in user_data and isinstance(user_data["last_login"], str) and user_data["last_login"]:
                        user_data["last_login"] = datetime.fromisoformat(user_data["last_login"])
                    
                    # Create UserInDB object
                    users[username] = UserInDB(**user_data)
                
                return users
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}
    
    def _save_users(self):
        """Save users to file."""
        try:
            # Convert UserInDB objects to dictionaries
            users_data = {}
            for username, user in self.users.items():
                # Convert to dictionary and handle datetime objects
                user_dict = user.dict()
                if isinstance(user_dict["created_at"], datetime):
                    user_dict["created_at"] = user_dict["created_at"].isoformat()
                if isinstance(user_dict["last_login"], datetime):
                    user_dict["last_login"] = user_dict["last_login"].isoformat()
                
                users_data[username] = user_dict
            
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(users_data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _create_admin_user(self):
        """Create an admin user if no users exist."""
        admin_password = os.environ.get("VALLUVARAI_ADMIN_PASSWORD") or "admin"
        admin_user = UserCreate(
            username="admin",
            email="admin@valluvarai.com",
            password=admin_password,
            full_name="ValluvarAI Admin"
        )
        
        user = self.create_user(admin_user)
        if user:
            # Update user to be an admin
            user_in_db = self.users.get(user.username)
            if user_in_db:
                user_in_db.is_admin = True
                self._save_users()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            plain_password: Plain text password.
            hashed_password: Hashed password.
            
        Returns:
            True if the password matches the hash, False otherwise.
        """
        if not self.enabled:
            return False
        
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Get password hash.
        
        Args:
            password: Plain text password.
            
        Returns:
            Hashed password.
        """
        if not self.enabled:
            return ""
        
        return self.pwd_context.hash(password)
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username.
            
        Returns:
            User if found, None otherwise.
        """
        if not self.enabled:
            return None
        
        user_in_db = self.users.get(username)
        if user_in_db:
            # Convert UserInDB to User (exclude hashed_password)
            user_dict = user_in_db.dict(exclude={"hashed_password"})
            return User(**user_dict)
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email.
            
        Returns:
            User if found, None otherwise.
        """
        if not self.enabled:
            return None
        
        for user in self.users.values():
            if user.email == email:
                # Convert UserInDB to User (exclude hashed_password)
                user_dict = user.dict(exclude={"hashed_password"})
                return User(**user_dict)
        
        return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            username: Username.
            password: Password.
            
        Returns:
            User if authentication is successful, None otherwise.
        """
        if not self.enabled:
            return None
        
        user_in_db = self.users.get(username)
        if not user_in_db:
            return None
        
        if not self.verify_password(password, user_in_db.hashed_password):
            return None
        
        # Update last login
        user_in_db.last_login = datetime.now()
        self._save_users()
        
        # Convert UserInDB to User (exclude hashed_password)
        user_dict = user_in_db.dict(exclude={"hashed_password"})
        return User(**user_dict)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create an access token.
        
        Args:
            data: Data to encode in the token.
            expires_delta: Token expiration time. If None, uses the default.
            
        Returns:
            JWT token.
        """
        if not self.enabled:
            return ""
        
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[TokenData]:
        """
        Decode a token.
        
        Args:
            token: JWT token.
            
        Returns:
            TokenData if decoding is successful, None otherwise.
        """
        if not self.enabled:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("sub")
            exp = datetime.fromtimestamp(payload.get("exp"))
            
            if username is None:
                return None
            
            return TokenData(username=username, exp=exp)
        except jwt.PyJWTError:
            return None
    
    def create_user(self, user_create: UserCreate) -> Optional[User]:
        """
        Create a new user.
        
        Args:
            user_create: User creation data.
            
        Returns:
            Created user if successful, None otherwise.
        """
        if not self.enabled:
            return None
        
        # Check if username already exists
        if user_create.username in self.users:
            return None
        
        # Check if email already exists
        for user in self.users.values():
            if user.email == user_create.email:
                return None
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = self.get_password_hash(user_create.password)
        
        user_in_db = UserInDB(
            id=user_id,
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            created_at=datetime.now(),
            preferences=UserPreferences(),
            usage_stats={"searches": 0, "stories_generated": 0, "images_generated": 0, "videos_generated": 0}
        )
        
        # Add user to users dictionary
        self.users[user_create.username] = user_in_db
        
        # Save users to file
        self._save_users()
        
        # Convert UserInDB to User (exclude hashed_password)
        user_dict = user_in_db.dict(exclude={"hashed_password"})
        return User(**user_dict)
    
    def update_user(self, username: str, user_update: UserUpdate) -> Optional[User]:
        """
        Update a user.
        
        Args:
            username: Username of the user to update.
            user_update: User update data.
            
        Returns:
            Updated user if successful, None otherwise.
        """
        if not self.enabled:
            return None
        
        # Check if user exists
        user_in_db = self.users.get(username)
        if not user_in_db:
            return None
        
        # Update user
        if user_update.email is not None:
            # Check if email already exists
            for user in self.users.values():
                if user.username != username and user.email == user_update.email:
                    return None
            
            user_in_db.email = user_update.email
        
        if user_update.full_name is not None:
            user_in_db.full_name = user_update.full_name
        
        if user_update.password is not None:
            user_in_db.hashed_password = self.get_password_hash(user_update.password)
        
        if user_update.preferences is not None:
            # Update only the provided preferences
            preferences_dict = user_update.preferences.dict(exclude_unset=True)
            for key, value in preferences_dict.items():
                setattr(user_in_db.preferences, key, value)
        
        # Save users to file
        self._save_users()
        
        # Convert UserInDB to User (exclude hashed_password)
        user_dict = user_in_db.dict(exclude={"hashed_password"})
        return User(**user_dict)
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user.
        
        Args:
            username: Username of the user to delete.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            return False
        
        # Check if user exists
        if username not in self.users:
            return False
        
        # Delete user
        del self.users[username]
        
        # Save users to file
        self._save_users()
        
        return True
    
    def update_usage_stats(self, username: str, stat_type: str, increment: int = 1) -> bool:
        """
        Update usage statistics for a user.
        
        Args:
            username: Username of the user.
            stat_type: Type of statistic to update (searches, stories_generated, etc.).
            increment: Amount to increment the statistic by.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            return False
        
        # Check if user exists
        user_in_db = self.users.get(username)
        if not user_in_db:
            return False
        
        # Update usage stats
        if stat_type not in user_in_db.usage_stats:
            user_in_db.usage_stats[stat_type] = 0
        
        user_in_db.usage_stats[stat_type] += increment
        
        # Save users to file
        self._save_users()
        
        return True
    
    def get_all_users(self, admin_only: bool = False) -> List[User]:
        """
        Get all users.
        
        Args:
            admin_only: Whether to only return admin users.
            
        Returns:
            List of users.
        """
        if not self.enabled:
            return []
        
        users = []
        for user_in_db in self.users.values():
            if admin_only and not user_in_db.is_admin:
                continue
            
            # Convert UserInDB to User (exclude hashed_password)
            user_dict = user_in_db.dict(exclude={"hashed_password"})
            users.append(User(**user_dict))
        
        return users
