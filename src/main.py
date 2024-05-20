from fileUtils.fileUtils import FileUtils
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
    FileUtils.save_to_disk(data)
    print("Finished!")
    return data


if __name__ == '__main__':
    run_script()
