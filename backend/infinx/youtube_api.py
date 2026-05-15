import os
import pickle
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger("infinx.youtube_api")

# Scopes needed for full YouTube Data API access (reading & posting to chat)
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

class YouTubeAPI:
    def __init__(self, client_secret_file: str):
        self.client_secret_file = client_secret_file
        self.youtube = None
        self.live_chat_id = None
        self.next_page_token = None

    def authenticate(self):
        """Authenticate with the YouTube Data API v3 via OAuth2."""
        creds = None
        token_path = os.path.join(os.path.dirname(self.client_secret_file), 'token.pickle')
        
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired YouTube OAuth token...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}. Will prompt for re-auth.")
                    creds = None

            if not creds:
                logger.info("Starting new OAuth flow. A browser window will open.")
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, SCOPES)
                # Use local server to capture the auth response
                creds = flow.run_local_server(port=0)
                
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
                
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info("Successfully authenticated with YouTube Data API v3.")

    def get_live_chat_id(self, video_id: str) -> str:
        """Fetch the liveChatId for a given YouTube video ID."""
        if not self.youtube:
            raise Exception("YouTube API not authenticated.")
            
        try:
            request = self.youtube.videos().list(
                part="liveStreamingDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                logger.error("Video not found.")
                return None
                
            details = response['items'][0].get('liveStreamingDetails')
            if not details or 'activeLiveChatId' not in details:
                logger.error("No active live chat found for this video. Is it currently live?")
                return None
                
            self.live_chat_id = details['activeLiveChatId']
            logger.info(f"Found liveChatId: {self.live_chat_id}")
            return self.live_chat_id
            
        except Exception as e:
            logger.error(f"Error fetching liveChatId: {e}")
            return None

    def poll_new_messages(self, live_chat_id: str = None) -> list:
        """Poll the live chat for new messages."""
        if not self.youtube:
            return []
            
        chat_id = live_chat_id or self.live_chat_id
        if not chat_id:
            return []
            
        try:
            request = self.youtube.liveChatMessages().list(
                liveChatId=chat_id,
                part="snippet,authorDetails",
                pageToken=self.next_page_token
            )
            response = request.execute()
            
            self.next_page_token = response.get('nextPageToken')
            messages = []
            
            for item in response.get('items', []):
                snippet = item['snippet']
                if snippet['type'] == 'textMessageEvent':
                    msg = snippet['textMessageDetails']['messageText']
                    author = item['authorDetails']['displayName']
                    messages.append({'author': author, 'text': msg})
                    
            return messages
            
        except Exception as e:
            logger.error(f"Error polling live chat messages: {e}")
            return []

    def post_message(self, text: str, live_chat_id: str = None) -> bool:
        """Post a message to the live chat via API."""
        if not self.youtube:
            logger.error("Cannot post message: API not authenticated.")
            return False
            
        chat_id = live_chat_id or self.live_chat_id
        if not chat_id:
            logger.error("Cannot post message: No active liveChatId.")
            return False
            
        try:
            request = self.youtube.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": text
                        }
                    }
                }
            )
            response = request.execute()
            logger.info(f"API Successfully posted message: '{text}'")
            return True
            
        except Exception as e:
            logger.error(f"API Error posting to live chat: {e}")
            return False
