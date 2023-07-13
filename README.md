# F-One
> Automatic Text-Generation with Deep Learning Models: a Chatbot based application.


This project aims to present the Conversational Assistant 
that we have developed, an Emotional Chatbot AI Question & Answer Text-Generation Knowledge-based, 
capable of handling conversations with users. The Chatbot is called “F-One” and is able to answer all 
questions related to the sport of Formula 1. Specifically, it is designed to provide information about the 
regulations of F1 and past as well as recent news.

---

<img
  src="docs/images/Website_with_F-One.png"
  alt="Alt text"
  title="Optional title"
  style="display: inline-block; margin: 0 auto; max-width: 300px">

---

## Project description

**Workflow**

  <p align="center">
  <img src="docs/images/F-One_Workflow.png" width="400">
  </p>

As the picture shows, the project may be divided into seven main phases:

 * [**Phase 1**: Training of the model](#phase-1-training-of-the-model)
 * [**Phase 2**: Input image segmentation and digits extraction](#phase-2-input-image-segmentation-and-digits-extraction)
 * [**Phase 3**: Long number recognition](#phase-3-long-number-recognition)
 * [**Phase 4**: Long number recognition](#phase-3-long-number-recognition)
 * [**Phase 5**: Long number recognition](#phase-3-long-number-recognition)
 * [**Phase 6**: Long number recognition](#phase-3-long-number-recognition)
 * [**Phase 7**: Long number recognition](#phase-3-long-number-recognition)
 

## Dev-Setup
Prerequisites:
- [Google CSE ID](https://programmablesearchengine.google.com/about/) - Free
- [Google API Key](https://cloud.google.com/docs/authentication/api-keys?hl=it) - Free
- [OpenAI API Key](https://platform.openai.com/account/api-keys) - Billing Required
- [Hugging Face Hub API Token](https://huggingface.co/docs/hub/index) - Free
- [Inspiredco API Key](https://docs.inspiredco.ai/critique/getting_started.html) - Free
- [Dialogflow 

## Requirements
Install dependencies:
```pip install -r requirements.txt```

## Project pipeline
1. [`preprocessing.py`](https://github.com/fp1acm8/SER/blob/main/preprocessing.py):\
Load the dataset and extract the audio features through the `librosa` library. Synthetic data were created in order to increase the number of audio samples through data augmentation techniques.
2. [`train.py`](https://github.com/fp1acm8/SER/blob/main/train.py):\
Train the MLP classifier defined in [`modules/mlp.py`](https://github.com/fp1acm8/SER/blob/main/models/mlp.py). But first the data must be prepared so that it can be input to the neural network. To do this, a special function called [`data_preparation()`](https://github.com/fp1acm8/SER/blob/main/modules/data_preparation.py) has been created.
3. [`predict.py`](https://github.com/fp1acm8/SER/blob/main/predict.py):\
Make predictions on data never seen by the model. Summary data of the predictions made can be found in the folder [`out/`](https://github.com/fp1acm8/SER/blob/main/out/).


Reference [example.env](https://github.com/filippoflorindi/F-One/blob/main/F-One/example.env) to create `.env` file
```python
GOOGLE_CSE_ID = ""
GOOGLE_API_KEY = ""
OPENAI_API_KEY = ""      
HUGGINGFACEHUB_API_TOKEN = "" 
INSPIREDCO_API_KEY = ""
```

## Credits

The F-One Chatbot was developed by [Filippo Florindi](https://github.com/filippoflorindi).
- E-mail: [filippo.florindi@gmail.com][mail]
- LinkedIn: [https://www.linkedin.com/in/filippo-florindi-130483259][linkedin]

## License

Do not Redistribute!

## Info

Link to this project: [https://github.com/filippoflorindi/F-One][project]

[project]: https://github.com/filippoflorindi/F-One
[mail]: filippo.florindi@gmail.com
[linkedin]: https://www.linkedin.com/in/filippo-florindi-130483259
