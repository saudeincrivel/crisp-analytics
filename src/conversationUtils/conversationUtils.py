
from typing import Any

ONE_SECOND = 6000


class ConversationUtils:
    @staticmethod
    def get_response_time_delay(chat_log) -> dict:
        client_first_message = None
        operator_first_message = None

        for message in chat_log:
            if message['from'] == "operator" and operator_first_message is None:
                operator_first_message = message['timestamp']
            elif message['from'] != "operator" and client_first_message is None:
                client_first_message = message['timestamp']

            if client_first_message is not None and operator_first_message is not None:
                break

        if operator_first_message != None and client_first_message != None:
            return (operator_first_message - client_first_message) / ONE_SECOND

        return None

    @staticmethod
    def get_last_message_timestamp(chat_log) -> Any:
        last_message_timestamp = None
        for message in chat_log:
            last_message_timestamp = message['timestamp']

        return last_message_timestamp

    @staticmethod
    def enrich_conversation(conversation, chat_log) -> Any:
        conversation_unix_start_time = conversation['created_at']
        last_message_timestamp = ConversationUtils.get_last_message_timestamp(chat_log)
        total_time_in_seconds = (last_message_timestamp - conversation_unix_start_time) / ONE_SECOND
        response_delay = ConversationUtils.get_response_time_delay(chat_log)

        enriched_conversation = {
            'session_id': conversation['session_id'],
            'start_time': conversation_unix_start_time,
            'response_delay': round(response_delay, 2) if response_delay else None,
            'total_time_in_seconds': round(total_time_in_seconds, 2)
        }

        return enriched_conversation
