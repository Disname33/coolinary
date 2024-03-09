import os
import subprocess

from django.http import JsonResponse, HttpRequest, HttpResponse

from coolinary.settings import BASE_DIR


def get_languages_from_dir(directory):
    """Return a list of directory names in the given directory."""
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]


BABEL_DEFAULT_LOCALE = 'en'
BABEL_LANGUAGES = get_languages_from_dir(os.path.join(BASE_DIR, 'locale'))


def create_babel(app):
    """Initialize localization settings."""
    app.config['BABEL_DEFAULT_LOCALE'] = BABEL_DEFAULT_LOCALE
    app.config['BABEL_LANGUAGES'] = BABEL_LANGUAGES


def get_locale(request: HttpRequest):
    """Get the user's locale from the request's accepted languages."""
    return HttpResponse(request.session.get('language') or request.META.get('HTTP_ACCEPT_LANGUAGE', '').split(',')[0])


def get_languages(request: HttpRequest):
    """Return a list of available languages in JSON format."""
    return JsonResponse({'languages': BABEL_LANGUAGES})


def compile_translations():
    """Compile the translation files."""
    result = subprocess.run(
        ['pybabel', 'compile', '-d', 'translations'],
        stdout=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise Exception(
            f'Compiling translations failed:\n{result.stdout.decode()}')

    print('Translations compiled successfully')
