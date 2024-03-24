#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def clear_logs():
    log_files = ['./logs/django.log']  # Замените пути к файлам логов на свои
    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'w') as file:
                file.write('')


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coolinary.settings')
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
    clear_logs()
    main()
