## =========================================================
## MS Version:
## ---------------------------------------------------------
#| 
#| import json
#| import requests
#| from flask import current_app
#| from flask_babel import _
#| 
#| def translate(text, source_language, target_language):
#| 
#|     if 'MS_TRANSLATOR_KEY' not in current_app.config or \
#|             not current_app.config['MS_TRANSLATOR_KEY']:
#|         return _('ERROR The translation service is not configured.')
#|     auth = {'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY']}
#|     r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
#|                      '/Translate?text={}&from={}&to={}'.format(
#|                          text, source_language, target_language),
#|                      headers=auth)
#|     if r.status_code != 200:
#|         return _('ERROR The translation service failed.')
#|     return json.loads(r.content.decode('utf-8-sig'))
#| 
## =========================================================
## Google Version:
## ---------------------------------------------------------

from google.cloud import translate as google_translate
from flask import current_app


def translate_text(text, source_language, target_language):
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
    if 'GOOGLE_TRANSLATION_PROJECT_ID' not in current_app.config or \
       not current_app.config['GOOGLE_TRANSLATION_PROJECT_ID']:
        return _('ERROR The translation service is not configured.')

    project_id = current_app.config['GOOGLE_TRANSLATION_PROJECT_ID']
    client = google_translate.TranslationServiceClient()
    parent = client.location_path(project_id, "global")

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        parent               = parent,
        contents             = text,
        mime_type            = "text/plain",  # mime types: text/plain, text/html
        source_language_code = source_language,
        target_language_code = target_language,
    )

    # Extract translations
    translated_text = []
    for translation in response.translations:
        #| print("DEBUG", translation)
        translated_text.append(translation.translated_text)

    return translated_text
        

def translate(string, source_language, target_language):
    """Translating Text."""

    # String to list of strings
    text = [ string ]

    # Translate
    translated_text = translate_text(text, source_language, target_language)

    # List of strings to string
    translation = ' '.join(translated_text)

    return translation


## fin.
