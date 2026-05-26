import tweepy
from urllib.parse import urlparse, parse_qs

CLIENT_ID = "x_api_oauth2_client_id"
CLIENT_SECRET = "x_api_oauth2_client_server"
REDIRECT_URI = "https://sicken.ai"       

SCOPES = ["tweet.read", "users.read", "tweet.write", "media.write", "offline.access"]

oauth2_handler = tweepy.OAuth2UserHandler(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    scope=SCOPES,
    client_secret=CLIENT_SECRET )

authorization_url = oauth2_handler.get_authorization_url()
print("1. Open this URL in your browser (log in as the account you want to post AS):")
print(authorization_url)
print("\n2. Authorize the app.")
print("3. After redirect, copy the FULL URL from your browser address bar (it starts with your redirect URI + ?code=...)")
print("   Paste it below.\n")


redirected_url = input("Paste the full redirect URL here: ").strip()

try:
    token_response = oauth2_handler.fetch_token(redirected_url)
    access_token = token_response["access_token"]
    refresh_token = token_response.get("refresh_token")  # Save this for later use!
    
    print("\nSuccess! Access Token:", access_token)
    if refresh_token:
        print("Refresh Token (save securely!):", refresh_token)
except Exception as e:
    print("Error fetching token:", e)
    exit(1)