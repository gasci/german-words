import json
import os
import boto3


class S3:
    def __init__(self):
        self.s3 = boto3.resource(
            service_name="s3",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )

        self.get_source_json()

    def get_source_json(self):

        self.obj = (
            self.s3.Bucket(os.environ["AWS_STORAGE_BUCKET_NAME"])
            .Object("other/vocab.json")
        )

        json_string = self.obj.get()["Body"].read().decode("utf-8")

        json_obj = json.loads(json_string)

        return json_obj

    def update_source_json(self, json_data):

        self.obj.put(Body=(bytes(json.dumps(json_data).encode("UTF-8"))))

        return self.obj
