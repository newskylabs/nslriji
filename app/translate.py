## =========================================================
## MS Version:
## ---------------------------------------------------------
#| 
#| import json
#| import requests
#| from flask_babel import _
#| from app import app
#| 
#| def translate_ms(text, source_language, dest_language):
#| 
#|     if 'TRANSLATION_CREDENTIALS' not in app.config or \
#|             not app.config['TRANSLATION_CREDENTIALS']:
#|         return _('Error: the translation service is not configured.')
#|     auth = {'Ocp-Apim-Subscription-Key': app.config['TRANSLATION_CREDENTIALS']}
#|     r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
#|                      '/Translate?text={}&from={}&to={}'.format(
#|                          text, source_language, dest_language),
#|                      headers=auth)
#|     if r.status_code != 200:
#|         return _('Error: the translation service failed.')
#|     return json.loads(r.content.decode('utf-8-sig'))
#| 
## =========================================================
## Google Version:
## ---------------------------------------------------------

from google.cloud import translate as google_translate
from app import app


def translate(text, source_language, dest_language):
    """Translating Text."""

    # See:
    # 
    #   - Translation
    #     https://cloud.google.com/translate
    #   - Translating text (Advanced)
    #     https://cloud.google.com/translate/docs/advanced/translating-text-v3#translating_text

    # NOTE:
    # The environment variable GOOGLE_APPLICATION_CREDENTIALS
    # has to be set to the path of the file containing the google application cedentials.

    # Get project ID
    if 'GOOGLE_TRANSLATION_PROJECT_ID' not in app.config or \
       not app.config['GOOGLE_TRANSLATION_PROJECT_ID']:
        return _('ERROR The translation service is not configured.')

    project_id = app.config['GOOGLE_TRANSLATION_PROJECT_ID']
    client = google_translate.TranslationServiceClient()
    parent = client.location_path(project_id, "global")
    # For parameter 'text' either strings of list of strings are accepted.
    # The 'contents' parameter, however, has to be a list of strings
    if isinstance(text, str):
        text = [ text ]

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        parent               = parent,
        contents             = text,
        mime_type            = "text/plain",  # mime types: text/plain, text/html
        source_language_code = source_language,
        target_language_code = dest_language,
    )

    # Extract translations
    translated_text = []
    for translation in response.translations:
        #| print("DEBUG", translation)
        translated_text.append(translation.translated_text)

    return translated_text
        
## fin.
