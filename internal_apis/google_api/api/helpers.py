import aiohttp
import subprocess
import io

from google.cloud import vision
from google.cloud import speech_v1 as speech
from google.cloud import translate
import google.auth


async def google_object_detection(file_url, headers):
    client = vision.ImageAnnotatorClient()
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.get(file_url, allow_redirects=True)
        response.raise_for_status()
        content = await response.read()
    image = vision.Image(dict(content=content))
    objects = client.object_localization(image=image)
    objects = objects.localized_object_annotations
    detected_objects = []
    for object_ in objects:
        # vertices = [vertex for vertex in object_.bounding_poly.normalized_vertices]
        detected_objects.append((object_.name, object_.score))
    return {
        "detected_objects": detected_objects
    }


def extract_text(image_content: bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(dict(content=image_content))
    response = client.text_detection(image=image)

    detected_text = []
    for text in response.text_annotations:
        extracted_text = text.description.replace("\n", " ").strip()
        print(extracted_text)
        detected_text.append(extracted_text)
        # vertices = ['(%s,%s)' % (v.x, v.y) for v in text.bounding_poly.vertices]
        # print('bounds:', ",".join(vertices))
    return detected_text


async def google_speech_to_text(file_url, headers, language_code):
    client = speech.SpeechClient()
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.get(file_url, allow_redirects=True)
        response.raise_for_status()
        content = await response.read()
    content = io.BytesIO(content)
    content.seek(0)
    command = ['ffmpeg', '-y', '-i', '-', '-f', 'flac', '-']
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    content, _ = process.communicate(content.read())
    audio = speech.RecognitionAudio(dict(content=content))
    config = speech.RecognitionConfig(
        dict(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            language_code=language_code,
            alternative_language_codes=["en-IN"]
        )
    )
    response = client.recognize(audio=audio, config=config)
    result = [{
        "transcript": result.alternatives[0].transcript,
        "confidence": result.alternatives[0].confidence,
        "detected_language_code": result.language_code
    }
        for result in response.results if len(result.alternatives) > 0]
    return result


def google_translate(data):
    _, PROJECT_ID = google.auth.default()
    PARENT = 'projects/{}'.format(PROJECT_ID)
    data["parent"] = PARENT
    TRANSLATE = translate.TranslationServiceClient()
    rsp = TRANSLATE.translate_text(**data)
    translation = rsp.translations[0]
    return {
        "detected_language": translation.detected_language_code,
        "translated_text": translation.translated_text,
        "translated_language": data.get("target_language_code")
    }

