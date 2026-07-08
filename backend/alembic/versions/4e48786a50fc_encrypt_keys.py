"""encrypt_keys

Revision ID: 4e48786a50fc
Revises: ccd02348c5de
Create Date: 2026-07-03 07:48:44.804810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import json
from cryptography.fernet import Fernet
from src.shared.config import app_settings


# revision identifiers, used by Alembic.
revision: str = '4e48786a50fc'
down_revision: Union[str, Sequence[str], None] = 'ccd02348c5de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    encryption_key = app_settings.ENCRYPTION_KEY
    if not encryption_key:
        print("WARNING: ENCRYPTION_KEY is not set. Cannot encrypt existing keys.")
        return
        
    fernet = Fernet(encryption_key)
    conn = op.get_bind()
    
    result = conn.execute(sa.text("SELECT id, private_key, oauth_config FROM projects"))
    projects = result.fetchall()
    
    for row in projects:
        project_id, private_key, oauth_config = row
        update_needed = False
        
        if private_key and not private_key.startswith("gAAAAAB"):
            private_key = fernet.encrypt(private_key.encode()).decode()
            update_needed = True
            
        new_oauth_config = {}
        if oauth_config:
            oauth_config_dict = json.loads(oauth_config) if isinstance(oauth_config, str) else oauth_config
                
            for provider, config in oauth_config_dict.items():
                if "client_secret" in config:
                    secret = config["client_secret"]
                    if secret and not secret.startswith("gAAAAAB"):
                        config["client_secret"] = fernet.encrypt(secret.encode()).decode()
                        update_needed = True
                new_oauth_config[provider] = config
                
        if update_needed:
            oauth_config_val = json.dumps(new_oauth_config) if new_oauth_config else None
            conn.execute(
                sa.text("UPDATE projects SET private_key = :pk, oauth_config = cast(:oc as jsonb) WHERE id = :pid"),
                {"pk": private_key, "oc": oauth_config_val, "pid": project_id}
            )


def downgrade() -> None:
    """Downgrade schema."""
    encryption_key = app_settings.ENCRYPTION_KEY
    if not encryption_key:
        return
        
    fernet = Fernet(encryption_key)
    conn = op.get_bind()
    
    result = conn.execute(sa.text("SELECT id, private_key, oauth_config FROM projects"))
    projects = result.fetchall()
    
    for row in projects:
        project_id, private_key, oauth_config = row
        update_needed = False
        
        if private_key and private_key.startswith("gAAAAAB"):
            private_key = fernet.decrypt(private_key.encode()).decode()
            update_needed = True
            
        new_oauth_config = {}
        if oauth_config:
            oauth_config_dict = json.loads(oauth_config) if isinstance(oauth_config, str) else oauth_config
                
            for provider, config in oauth_config_dict.items():
                if "client_secret" in config:
                    secret = config["client_secret"]
                    if secret and secret.startswith("gAAAAAB"):
                        config["client_secret"] = fernet.decrypt(secret.encode()).decode()
                        update_needed = True
                new_oauth_config[provider] = config
                
        if update_needed:
            oauth_config_val = json.dumps(new_oauth_config) if new_oauth_config else None
            conn.execute(
                sa.text("UPDATE projects SET private_key = :pk, oauth_config = cast(:oc as jsonb) WHERE id = :pid"),
                {"pk": private_key, "oc": oauth_config_val, "pid": project_id}
            )
