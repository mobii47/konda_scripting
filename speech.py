import azure.cognitiveservices.speech as speechsdk
from argparse import ArgumentParser
from time import sleep
import os
from dotenv import load_dotenv

load_dotenv()

# GLOBALS
SPEECH_KEY = os.environ.get("SPEECH_KEY")
REGION = os.environ.get("REGION")
src_lang_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=[
        "en-US",
        "fr-FR",
        "de-DE",
        "es-ES",
    ]
)
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=REGION)
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config, auto_detect_source_language_config=src_lang_config
)


def run_asr():
    # Instantiate speech recognizer

    def log_asr(evt, status):
        detected_src_lang = evt.result.properties.get(
            speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult,
            "Unknown",
        )
        text = evt.result.text
        if len(text) > 0:
            print(f"{status.upper()}:     {detected_src_lang}     {text}")

    # Code to stop continuous recognition
    done = False

    def stop_cb(evt):
        print(f"Closing on {evt}")
        speech_recognizer.stop_continuous_recognition()
        # nonlocal done
        done = True

    speech_recognizer.recognizing.connect(lambda evt: log_asr(evt, "temporary"))
    speech_recognizer.recognized.connect(lambda evt: log_asr(evt, "final"))
    speech_recognizer.session_started.connect(
        lambda evt: print(f"SESSION STARTED: {evt}")
    )
    speech_recognizer.session_stopped.connect(
        lambda evt: print(f"SESSION STOPPED {evt}")
    )
    speech_recognizer.canceled.connect(lambda evt: print(f"CANCELED {evt}"))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)
    speech_recognizer.start_continuous_recognition_async()

    while not done:
        sleep(0.2)


if __name__ == "__main__":
    parser = ArgumentParser("run azure asr.")
    args = parser.parse_args()
    run_asr()
