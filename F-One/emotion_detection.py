
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline

tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")


def emotion_classifier(input_query):

    emotion = pipeline('sentiment-analysis', 
                        model='arpanghoshal/EmoRoBERTa',
                        #return_all_scores= True
                        )

    emotion_labels = emotion(input_query)
    return emotion_labels[0] 



if __name__ == "__main__":

    input_query = "I'm not agree with the FIA decisions"

    emotion_labels = emotion_classifier(input_query)
    print("\n\n")
    print(emotion_labels)
    print("\n")
    print(emotion_labels['label'])
    print(emotion_labels['score'])