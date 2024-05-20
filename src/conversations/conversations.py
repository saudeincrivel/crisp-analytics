from crisp_api import Crisp
from config.settings import IDENTIFIER, KEY, SECRET, SITE_ID
from conversationUtils.conversationUtils import ConversationUtils
import time
import logging
import requests
from typing import Any

logger = logging.getLogger(__name__)


class ConversationsAPI:
    def __init__(self, id=IDENTIFIER, key=KEY, secret=SECRET, site_id=SITE_ID) -> None:
        self.identifier = id
        self.key = key
        self.secret = secret
        self.site_id = site_id

        client = Crisp()
        client.set_tier("plugin")
        client.authenticate(self.identifier, self.key)

        self.client = client

    def get_all_conversations(self, start_time=None, end_time=None) -> Any:
        print('running method: get_all_conversations...')
        try:
            params = {'page_number': '1', 'website_id': self.site_id}
            all_conversations = []

            while True:
                if start_time:
                    params['filter_date_start'] = start_time
                if end_time:
                    params['filter_date_end'] = end_time

                try:
                    print(f'Request conversations ...')
                    conversations = self.client.website.list_conversations(**params)
                except Exception as e:
                    print("Error occurred while fetching conversations:", e)
                    break

                all_conversations.extend(conversations)

                if not conversations:
                    break

                params['page_number'] = str(int(params['page_number']) + 1)

                time.sleep(0.1)

            return all_conversations

        except Exception as e:
            print("Error:", e)

    def get_all_conversation_sessions(self) -> list[str]:
        try:
            conversations = self.get_all_conversations()

            if 'error' in conversations:
                logger.error(f"[API error] in get_all_conversation_sessions : {conversations['reason']}")
                raise Exception(f"[API error] in get_all_conversation_sessions : {conversations['reason']}")

            session_ids = [conversation['session_id'] for conversation in conversations['data']]

            return session_ids
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get all conversation sessions", exc_info=True)
            raise

    def get_messages(self, session_id) -> Any:
        try:
            chat_log = self.client.website.get_messages_in_conversation(self.site_id, session_id, {})

            if 'error' in chat_log:
                logger.error(f"[API error] in get_messages : {chat_log['reason']}")
                raise Exception(f"[API error]: {chat_log['reason']}")

            return chat_log
        except requests.exceptions.RequestException as e:
            logger.error("[Request Error] in get_messages")
        pass

    def get_enriched_conversations(self, start_time=None, end_time=None) -> list[Any]:
        DELAY = 0.3
        enriched_conversations = []
        conversations = self.get_all_conversations(start_time, end_time)

        for conversation in conversations:
            if conversation['state'] == 'resolved':
                print("Getting messages...")
                chat_log = self.get_messages(conversation['session_id'])
                enriched_conversations.append(ConversationUtils.enrich_conversation(conversation, chat_log))
                time.sleep(DELAY)

        return enriched_conversations
