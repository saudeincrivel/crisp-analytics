from typing import Any, Dict
ONE_SECOND = 6000


class ConversationUtils:
    @staticmethod
    def remove_outliers(data):
        if not data:
            return data

        response_times = [item['avg_response_time'] for item in data]

        sorted_times = sorted(response_times)

        def calculate_quartile(data, q):
            pos = (len(data) - 1) * q
            lower = int(pos)
            upper = lower + 1
            weight = pos - lower
            if upper < len(data):
                return data[lower] * (1 - weight) + data[upper] * weight
            else:
                return data[lower]

        Q1 = calculate_quartile(sorted_times, 0.25)
        Q3 = calculate_quartile(sorted_times, 0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        filtered_data = [item for item in data if lower_bound <= item['avg_response_time'] <= upper_bound]

        return filtered_data

    @staticmethod
    def get_average_response_time(chat_log) -> Any:
        user_message = None
        operator_message = None
        computed = False

        count = 0
        delay_summation = 0
        print("Number of messages read: ", len(chat_log))

        def accumulate():
            nonlocal computed, count, delay_summation, user_message, operator_message
            difference = operator_message - user_message
            if difference > 0:
                count += 1
                delay_summation += difference
                computed = True

        def reset():
            nonlocal computed, user_message, operator_message
            computed = False
            user_message = None
            operator_message = None

        for message in chat_log:
            if not user_message:
                if message['from'] == 'user':
                    user_message = message['timestamp']

            if not computed and user_message and not operator_message:
                if message['from'] == 'operator':
                    operator_message = message['timestamp']
                    accumulate()

            if 'namespace' in message['content']:
                if 'state:resolved' in message['content']['namespace']:
                    reset()

        avg = delay_summation / count if count > 0 else 0
        return avg / ONE_SECOND

    @staticmethod
    def get_first_timestamp(partial_log) -> Any:
        if partial_log:
            return partial_log[0]['timestamp']

        return 0

    @staticmethod
    def get_last_message_timestamp(chat_log) -> Any:
        last_message_timestamp = None
        for message in chat_log:
            last_message_timestamp = message['timestamp']

        return last_message_timestamp

    @staticmethod
    def sort_chat_messages(chat_log) -> Any:
        sorted_log = sorted(chat_log, key=lambda x: x.get('timestamp', 0))
        return sorted_log

    @staticmethod
    def enrich_conversation(conversation, chat_log) -> Any:
        conversation_unix_start_time = conversation['created_at']
        last_message_timestamp = ConversationUtils.get_last_message_timestamp(chat_log)

        total_time_in_seconds = None
        if last_message_timestamp and conversation_unix_start_time:
            total_time_in_seconds = (last_message_timestamp - conversation_unix_start_time) / ONE_SECOND

        avg_response_time = ConversationUtils.get_average_response_time(chat_log)

        enriched_conversation = {
            'session_id': conversation['session_id'],
            'start_time': conversation_unix_start_time,
            'avg_response_time': round(avg_response_time, 2) if avg_response_time else None,
            'total_time_in_seconds': round(total_time_in_seconds, 2) if total_time_in_seconds else None,
            'number_of_messages': len(chat_log)
        }

        return enriched_conversation
