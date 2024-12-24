import signal
from final.chat import ChatBot
import sys

# intent_avg: 0.9786511479591837 def slot_avg: 0.9956899314657061

def quit_handler(signum, frame):
    print('\nBye~')
    sys.exit()


if __name__ == '__main__':
    chat_bot = ChatBot(7689)
    signal.signal(signal.SIGINT, quit_handler)

    print(chat_bot.self_intro())
    
    while True:
        question = input('你:')
        
        answer = chat_bot.chat(question)
        print('Bot:', answer)

