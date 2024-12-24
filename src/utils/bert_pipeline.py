from data.build_dataset import build_dataset
from NLP.bert_intent_slot.data.DouBanTop250.extract_labels import extract_lables
from NLP.bert_intent_slot.train import main


def pipeline():
    print("build_dataset")
    build_dataset()
    print("extract_lables")
    extract_lables()
    print("train main")
    main()

if __name__ == '__main__':
    pipeline()