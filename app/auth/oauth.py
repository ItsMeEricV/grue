from flask import Flask
from authlib.integrations.flask_client import OAuth

# Instantiate OAuth and store it in the app's extensions
# Then register the Google openid connect provider
def register_oauth(app: Flask) -> None:
    oauth = OAuth(app)
    app.extensions['oauth'] = oauth

    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        authorize_params=None,
        access_token_params=None,
        refresh_token_url=None,
        redirect_uri=app.config['GOOGLE_CALLBACK'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid profile email',
            'audience': app.config['GOOGLE_CLIENT_ID']
        }
    )