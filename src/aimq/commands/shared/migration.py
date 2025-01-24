from pathlib import Path
from typing import Optional, Dict, Any
import os
from langchain_core.utils.mustache import render

from .paths import ProjectPath

class SupabaseMigrations:
    def __init__(self, project_path: ProjectPath):
        """
        Initialize Migration with a ProjectPath instance.
        
        Args:
            project_path (ProjectPath): Instance of ProjectPath for file operations
        """
        self.project_path = project_path
        self.template_dir = Path(__file__).parent / "templates"

    def _get_template(self, template_name: str) -> Path:
        """
        Get the template path from the library's templates directory.
        
        Args:
            template_name (str): Name of the template file
            
        Returns:
            Path: Path to the template file
        """
        template_path = self.template_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found in {self.template_dir}")
                
        return template_path

    def create_migration(self, name: str, template_name: str, context: Optional[Dict[str, Any]] = None) -> Path:
        """
        Create a new migration file from a template.
        
        Args:
            name (str): Name of the migration
            template_name (str): Name of the template file to use
            context (Optional[Dict[str, Any]]): Context data to apply to the template
            
        Returns:
            Path: Path to the created migration file
        """
        context = context or {}
        
        # Check for existing migration using ProjectPath
        existing = self.project_path.find_existing_migration(name)
        if existing:
            return existing
            
        # Get template from library
        template_path = self._get_template(template_name)
            
        # Generate migration path using ProjectPath
        migration_path = self.project_path.migration_path(name)
        
        # Ensure migrations directory exists
        os.makedirs(self.project_path.migrations, exist_ok=True)
        
        # Load and render template
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        content = render(template_content, context)
        
        # Write migration file
        with open(migration_path, 'w') as f:
            f.write(content)
            
        return migration_path

    def setup_aimq_migration(self) -> Path:
        """
        Create the enable AIMQ migration using the static template.
        This migration enables the necessary Supabase configuration for AIMQ.
        
        Returns:
            Path: Path to the created migration file
        """
        return self.create_migration(
            name="setup_aimq",
            template_name="setup_aimq.sql"
        )

    def create_queue_migration(self, queue_name: str) -> Path:
        """
        Create a queue-specific migration.
        This migration sets up a new queue with the specified name.
        
        Args:
            queue_name (str): Name of the queue to create
            
        Returns:
            Path: Path to the created migration file
        """
        return self.create_migration(
            name=f"create_queue_{queue_name}",
            template_name="create_queue.sql",
            context={"queue_name": queue_name}
        )