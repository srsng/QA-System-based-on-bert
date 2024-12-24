import json

def extract_lables():
    with open(r'src\NLP\bert_intent_slot\data\DouBanTop250\data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)

    intent_labels = ['[UNK]']
    slot_labels = ['[PAD]','[UNK]', '[O]']
    for item in data:
        if item['intent'] not in intent_labels:
            intent_labels.append(item['intent'])

        for slot_name, slot_value in item['slots'].items():
            if 'B_'+slot_name not in slot_labels:
                slot_labels.extend(['I_'+slot_name, 'B_'+slot_name])

    with open(r'src\NLP\bert_intent_slot\data\DouBanTop250\slot_labels.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(slot_labels))

    with open(r'src\NLP\bert_intent_slot\data\DouBanTop250\intent_labels.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(intent_labels))

if __name__ == '__main__':
    extract_lables()