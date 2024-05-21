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
        self.total = 0
        self.processed = 0
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

                failedRequest = True
                attempts = 0
                while failedRequest and attempts < 3:
                    try:
                        print(f'Requesting conversations... Attempt {attempts + 1}')
                        conversations = self.client.website.search_conversations(**params)
                        failedRequest = False
                    except Exception as e:
                        print(f"Error occurred while fetching conversations: {e}")
                        attempts += 1
                        time.sleep(1)

                if attempts == 3:
                    raise Exception("Failed to fetch conversations after 3 attempts")

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
        complete_chat_log = []
        my_timestamp = int(time.time()) * 1000

        def fetch_messages(site_id, session_id, timestamp):
            query = {
                'timestamp_before': timestamp
            }

            failedRequest = True
            attempts = 0
            while failedRequest and attempts < 3:
                try:
                    response = self.client.website.get_messages_in_conversation(site_id, session_id, query)
                    failedRequest = False
                except Exception as e:
                    attempts += 1
                    failedRequest = True
                    print(f'[Request error]:', e)

            return response

        try:
            while True:
                try:
                    partial_chat_log = fetch_messages(self.site_id, session_id, my_timestamp)

                    if not partial_chat_log:
                        break

                    my_timestamp = ConversationUtils.get_first_timestamp(partial_chat_log)

                except Exception as e:
                    print("Request error. while fetching messages: ", e)
                    break

                if 'error' in partial_chat_log:
                    logger.error(f"[API error] in get_messages ")
                    raise Exception(f"[API error]: {partial_chat_log['reason']}")

                complete_chat_log.extend(partial_chat_log)
            return complete_chat_log

        except requests.exceptions.RequestException as e:
            logger.error("[API error] in partial_chat_log")
        pass

    def get_enriched_conversations(self, start_time=None, end_time=None) -> list[Any]:
        DELAY = 0.1
        enriched_conversations = []
        conversations = self.get_all_conversations(start_time, end_time)
        self.total = len ( conversations)

        for conversation in conversations:
            print(self.processed , " conversas de total aproximado :", self.total);
            if conversation['state'] == 'resolved':
                print("Getting messages...")
                chat_log = self.get_messages(conversation['session_id'])
                chat_log = ConversationUtils.sort_chat_messages(chat_log)
                enriched_conversations.append(ConversationUtils.enrich_conversation(conversation, chat_log))
                time.sleep(DELAY)
            self.processed+=1
        return enriched_conversations
