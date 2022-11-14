import json
import urllib.parse
import boto3
import os
import re


MEDIA_ENDPOINT = os.getenv("MEDIA_ENDPOINT")
MEDIA_ROLE = os.getenv("MEDIA_ROLE")
TRANSCODED_VIDEOS_PATH = os.getenv("TRANSCODED_VIDEOS_PATH")

media_client = boto3.client('mediaconvert', endpoint_url=MEDIA_ENDPOINT)


def transcoder(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

        match = re.match(r".*/(.*)\..*", key)
        file_name = match.groups()[0] if match else "test"

        source_path = f"s3://{bucket}/{key}"
        target_path = f"s3://{bucket}/{TRANSCODED_VIDEOS_PATH}/{file_name}/"
        transcode_video_job = get_media_convert_job(source_path, target_path)

        response = media_client.create_job(**transcode_video_job)
        return "Success"
    except Exception as e:
        print(e)
        raise e


def get_media_convert_job(source, target):
    return {
            "Role": MEDIA_ROLE,
            "Settings": {
                "Inputs": [{
                    "FileInput": source,
                    "AudioSelectors": {
                        "Audio Selector 1": {
                            "SelectorType": "TRACK",
                            "Tracks": [1]
                        }
                    }
                }],
                "OutputGroups": [{
                    "Name": "File Group",
                    "Outputs": [{
                        "Preset": "System-Generic_Hd_Mp4_Avc_Aac_16x9_1920x1080p_24Hz_6Mbps",
                        "Extension": "mp4",
                        "NameModifier": "_16x9_1920x1080p_24Hz_6Mbps"
                    }, {
                        "Preset": "System-Generic_Hd_Mp4_Avc_Aac_16x9_1280x720p_24Hz_4.5Mbps",
                        "Extension": "mp4",
                        "NameModifier": "_16x9_1280x720p_24Hz_4.5Mbps"
                    }, {
                        "Preset": "System-Generic_Sd_Mp4_Avc_Aac_4x3_640x480p_24Hz_1.5Mbps",
                        "Extension": "mp4",
                        "NameModifier": "_4x3_640x480p_24Hz_1.5Mbps"
                    }],
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_SETTINGS",
                        "FileGroupSettings": {
                            "Destination": target
                        }
                    }
                }]
            }
        }
