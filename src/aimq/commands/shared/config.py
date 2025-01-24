import shutil
import tomlkit
from tomlkit import TOMLDocument, items
from pathlib import Path
from typing import Dict, Any

from .paths import ProjectPath


class SupabaseConfig:
    def __init__(self, project_path: ProjectPath):
        """
        Initialize SupabaseConfig with a ProjectPath instance.

        Args:
            project_path (ProjectPath): Instance of ProjectPath for path management
        """
        self.project_path = project_path
        self._config: TOMLDocument = tomlkit.document()

    @property
    def config(self) -> TOMLDocument:
        """
        Get the config, loading it if not already loaded.

        Returns:
            TOMLDocument: The loaded configuration
        """
        if not self._config:
            self.load()
        return self._config

    def load(self) -> TOMLDocument:
        """
        Load the Supabase config from config.toml file.
        Creates config from template if it doesn't exist.
        Ensures api.schemas exists in the config.

        Returns:
            TOMLDocument: Loaded configuration
        """
        if not self.project_path.supabase_config.exists():
            self._create_from_template()

        with open(self.project_path.supabase_config, "r") as f:
            self._config = tomlkit.load(f)

        # Ensure api.schemas exists
        if "api" not in self._config:
            self._config.add("api", tomlkit.table())

        api_table: items.Table = self._config["api"]  # type: ignore
        if "schemas" not in api_table:
            api_table.add("schemas", tomlkit.array())

        return self._config

    def save(self) -> None:
        """Save the current configuration back to config.toml"""
        with open(self.project_path.supabase_config, "w") as f:
            tomlkit.dump(self.config, f)

    def _create_from_template(self) -> None:
        """Create a new config.toml from the template"""
        template_path = Path(__file__).parent / "templates" / "config.toml"
        self.project_path.supabase.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_path, self.project_path.supabase_config)

    def enable(self) -> None:
        """Enable PGMQ in Supabase by adding pgmq_public to API schemas"""
        schemas: items.Array = self.config["api"]["schemas"]  # type: ignore
        if "pgmq_public" not in schemas:
            schemas.append("pgmq_public")
            self.save()

    def disable(self) -> None:
        """Disable PGMQ in Supabase by removing pgmq_public from API schemas"""
        schemas: items.Array = self.config["api"]["schemas"]  # type: ignore
        if "pgmq_public" in schemas:
            schemas.remove("pgmq_public")
            self.save()

