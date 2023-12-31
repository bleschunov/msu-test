import os
from typing import BinaryIO, Generator

import requests
from dotenv import load_dotenv

load_dotenv()


class ChatPdfService:
    url = "https://api.chatpdf.com/v1/chats/message"
    upload_file_url = "https://api.chatpdf.com/v1/sources/add-file"
    headers = {
        "x-api-key": os.getenv("CHAT_PDF_API_KEY"),
    }

    @classmethod
    def run(cls, messages, source_id) -> Generator:
        try:
            response = requests.post(
                cls.url,
                json=cls.create_body(messages, source_id),
                headers={
                    **cls.headers,
                    "Content-Type": "application/json"
                },
                stream=True
            )
            response.raise_for_status()

            if response.iter_content:
                max_chunk_size = 1024
                for chunk in response.iter_content(max_chunk_size):
                    text = chunk.decode()
                    yield text
            else:
                raise Exception("No data received")
        except requests.exceptions.RequestException as error:
            print("Error:", error)

    @classmethod
    def create_user_message(cls, content):
        return {
            "role": "user",
            "content": content
        }

    @classmethod
    def create_assistant_message(cls, content):
        return {
            "role": "assistant",
            "content": content
        }

    @classmethod
    def create_body(cls, messages, source_id):
        return {
            "stream": True,
            "sourceId": source_id,
            "messages": messages
        }

    @classmethod
    def upload_file(cls, file: BinaryIO) -> str:
        files = [(
            'file',
            (
                'file',
                file,
                'application/octet-stream'
            )
        )]

        response = requests.post(
            cls.upload_file_url,
            headers=cls.headers,
            files=files,
            stream=True
        )
        response.raise_for_status()

        if response.json:
            responseData = response.json()
            source_id = responseData["sourceId"]
            return source_id
        else:
            raise Exception("No sourceId received")


if __name__ == "__main__":
    messages = [
        {
            "role": "user",
            "content": "Как воспроизводится купонная выплата?",
        },
    ]
    source_id = os.getenv("CHAT_PDF_API_KEY")

    for chunk in ChatPdfService.run(messages, source_id):
        print(chunk)
