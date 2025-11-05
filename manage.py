#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Auto-activate virtual environment if it exists
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv')
    if os.path.exists(venv_path):
        # Add virtual environment's site-packages to Python path
        import site
        site_packages = os.path.join(venv_path, 'lib', 'python3.13', 'site-packages')
        if os.path.exists(site_packages):
            site.addsitedir(site_packages)
        
        # Update PATH to include virtual environment's bin directory
        venv_bin = os.path.join(venv_path, 'bin')
        if venv_bin not in os.environ.get('PATH', ''):
            os.environ['PATH'] = venv_bin + ':' + os.environ.get('PATH', '')
        
        # Set VIRTUAL_ENV environment variable
        os.environ['VIRTUAL_ENV'] = venv_path
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market_nearby.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
