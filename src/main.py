from fileUtils.fileUtils import FileUtils
from conversationUtils.conversationUtils import ConversationUtils
from dateUtils.dateUtils import convert_to_iso
from conversations.conversations import ConversationsAPI
import logging
import sys
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)


def run_script():
    print("Running program..")
    api = ConversationsAPI()
    data = api.get_enriched_conversations()
    filtered_data = ConversationUtils.remove_outliers(data)
    FileUtils.save_to_disk(filtered_data)

    print("Finished!")
    return data


def run_script_with_filter(start_time, end_time):
    print(f'Running with filter dates: {start_time} , {end_time}')
    api = ConversationsAPI()
    data = api.get_enriched_conversations(convert_to_iso(start_time), convert_to_iso(end_time))
    FileUtils.save_to_disk(data)
    print("Finished")
    pass


if __name__ == '__main__':
    # start_time = '20/04/2024'
    # end_time = '20/05/2024'
    # run_script_with_filter(start_time, end_time)

    run_script()
