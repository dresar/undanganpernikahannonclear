#!/usr/bin/env python
"""
Script untuk migrasi data template dari template_editor ke admin_panel
dan menghubungkan kedua aplikasi melalui SQLite database.
"""

import os
import sys
import django
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wedding_invitation_platform.settings')
django.setup()

from django.contrib.auth.models import User
from template_editor.models import (
    Template as EditorTemplate, 
    TemplateCategory as EditorTemplateCategory,
    TemplateTag as EditorTemplateTag,
    TemplateCustomization,
    TemplateRating,
    TemplateLike,
    TemplateDownload,
    AIGenerationHistory as EditorAIHistory
)
from admin_panel.models import (
    TemplateCategory as AdminTemplateCategory,
    TemplateTag as AdminTemplateTag,
    TemplateVersion,
    AIGenerationHistory as AdminAIHistory,
    ActivityLog
)
from main.models import InvitationTemplate, Order, InvitationData

def log_migration_activity(action, description):
    """Log migration activities"""
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            ActivityLog.objects.create(
                user=admin_user,
                action=action,
                model_name='Migration',
                description=description
            )
    except Exception as e:
        print(f"Warning: Could not log activity - {e}")

def migrate_categories():
    """Migrate template categories from editor to admin panel"""
    print("Migrating template categories...")
    
    migrated_count = 0
    
    for editor_category in EditorTemplateCategory.objects.all():
        admin_category, created = AdminTemplateCategory.objects.get_or_create(
            name=editor_category.name,
            defaults={
                'description': editor_category.description,
                'is_active': editor_category.is_active,
                'sort_order': editor_category.sort_order if hasattr(editor_category, 'sort_order') else 0
            }
        )
        
        if created:
            migrated_count += 1
            print(f"  Created category: {admin_category.name}")
    
    log_migration_activity('migrate', f'Migrated {migrated_count} template categories')
    print(f"Migrated {migrated_count} categories")

def migrate_tags():
    """Migrate template tags from editor to admin panel"""
    print("Migrating template tags...")
    
    migrated_count = 0
    
    for editor_tag in EditorTemplateTag.objects.all():
        admin_tag, created = AdminTemplateTag.objects.get_or_create(
            name=editor_tag.name,
            defaults={
                'description': getattr(editor_tag, 'description', ''),
                'color': getattr(editor_tag, 'color', '#3B82F6')
            }
        )
        
        if created:
            migrated_count += 1
            print(f"  Created tag: {admin_tag.name}")
    
    log_migration_activity('migrate', f'Migrated {migrated_count} template tags')
    print(f"Migrated {migrated_count} tags")

def migrate_templates():
    """Migrate templates from editor to main app"""
    print("Migrating templates...")
    
    migrated_count = 0
    
    for editor_template in EditorTemplate.objects.all():
        # Check if template already exists in main app
        existing_template = InvitationTemplate.objects.filter(
            name=editor_template.name
        ).first()
        
        if not existing_template:
            # Create new template in main app
            main_template = InvitationTemplate.objects.create(
                name=editor_template.name,
                description=editor_template.description,
                html_content=editor_template.html_content,
                css_content=editor_template.css_content,
                js_content=editor_template.js_content,
                thumbnail_url=editor_template.thumbnail_url if hasattr(editor_template, 'thumbnail_url') else '',
                price=getattr(editor_template, 'price', 0),
                is_premium=getattr(editor_template, 'is_premium', False),
                is_featured=getattr(editor_template, 'is_featured', False),
                status=getattr(editor_template, 'status', 'active'),
                created_at=editor_template.created_at,
                updated_at=editor_template.updated_at
            )
            
            # Create template version in admin panel
            TemplateVersion.objects.create(
                template_name=main_template.name,
                version_number='1.0.0',
                html_content=main_template.html_content,
                css_content=main_template.css_content,
                js_content=main_template.js_content,
                changelog='Initial migration from template editor',
                is_active=True,
                created_by=editor_template.author if hasattr(editor_template, 'author') else None
            )
            
            migrated_count += 1
            print(f"  Migrated template: {main_template.name}")
    
    log_migration_activity('migrate', f'Migrated {migrated_count} templates')
    print(f"Migrated {migrated_count} templates")

def migrate_ai_history():
    """Migrate AI generation history"""
    print("Migrating AI generation history...")
    
    migrated_count = 0
    
    for editor_history in EditorAIHistory.objects.all():
        admin_history, created = AdminAIHistory.objects.get_or_create(
            user=editor_history.user,
            input_prompt=editor_history.input_prompt,
            created_at=editor_history.created_at,
            defaults={
                'processed_prompt': getattr(editor_history, 'processed_prompt', editor_history.input_prompt),
                'ai_response': getattr(editor_history, 'ai_response', ''),
                'parameters': getattr(editor_history, 'parameters', {}),
                'status': getattr(editor_history, 'status', 'completed'),
                'error_message': getattr(editor_history, 'error_message', ''),
                'completed_at': getattr(editor_history, 'completed_at', editor_history.created_at)
            }
        )
        
        if created:
            migrated_count += 1
            print(f"  Migrated AI history: {admin_history.input_prompt[:50]}...")
    
    log_migration_activity('migrate', f'Migrated {migrated_count} AI generation records')
    print(f"Migrated {migrated_count} AI generation records")

def create_admin_integration():
    """Create integration settings between template editor and admin panel"""
    print("Creating admin panel integration...")
    
    from admin_panel.models import SystemSettings
    
    # Create system settings for template editor integration
    settings_data = {
        'template_editor_enabled': True,
        'auto_sync_templates': True,
        'template_approval_required': False,
        'max_templates_per_user': 50,
        'template_storage_path': 'templates/',
        'backup_templates': True
    }
    
    for key, value in settings_data.items():
        setting, created = SystemSettings.objects.get_or_create(
            key=key,
            defaults={'value': str(value)}
        )
        if created:
            print(f"  Created setting: {key} = {value}")
    
    log_migration_activity('configure', 'Created template editor integration settings')
    print("Integration settings created")

def update_database_connections():
    """Update database connections - SQLite checks commented out for MySQL migration"""
    print("Updating database connections...")
    
    from django.conf import settings
    
    # Verify database engine (updated for MySQL)
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'mysql' in db_engine:
        print(f"  ✓ Using MySQL database: {settings.DATABASES['default']['NAME']}")
    else:
        print(f"  ⚠ Warning: Not using MySQL. Current engine: {db_engine}")
    
    # SQLite checks commented out for MySQL migration
    # # Verify SQLite is being used
    # db_engine = settings.DATABASES['default']['ENGINE']
    # if 'sqlite' in db_engine:
    #     print(f"  ✓ Using SQLite database: {settings.DATABASES['default']['NAME']}")
    # else:
    #     print(f"  ⚠ Warning: Not using SQLite. Current engine: {db_engine}")
    # 
    # # Check database file exists and is writable
    # db_path = settings.DATABASES['default']['NAME']
    # if os.path.exists(db_path):
    #     print(f"  ✓ Database file exists: {db_path}")
    #     if os.access(db_path, os.W_OK):
    #         print(f"  ✓ Database file is writable")
    #     else:
    #         print(f"  ⚠ Warning: Database file is not writable")
    # else:
    #     print(f"  ⚠ Warning: Database file does not exist: {db_path}")

def main():
    """Main migration function"""
    print("Starting template migration process...")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            # Update database connections
            update_database_connections()
            
            # Migrate data
            migrate_categories()
            migrate_tags()
            migrate_templates()
            migrate_ai_history()
            
            # Create integration
            create_admin_integration()
            
            print("=" * 50)
            print("Migration completed successfully!")
            print("\nSummary:")
            print(f"- Template categories: {AdminTemplateCategory.objects.count()}")
            print(f"- Template tags: {AdminTemplateTag.objects.count()}")
            print(f"- Templates: {InvitationTemplate.objects.count()}")
            print(f"- Template versions: {TemplateVersion.objects.count()}")
            print(f"- AI generation history: {AdminAIHistory.objects.count()}")
            
            log_migration_activity('complete', 'Template migration completed successfully')
            
    except Exception as e:
        print(f"Migration failed: {e}")
        log_migration_activity('error', f'Migration failed: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()