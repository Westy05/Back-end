from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import boto3
from botocore.exceptions import ClientError, ParamValidationError
import os
from dotenv import load_dotenv

load_dotenv("bedrock/.env")

app = Flask(__name__)

api = Api(app)

access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

dynamodb = boto3.client(
    service_name='dynamodb',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name='us-west-2',
)

class GetItem(Resource):
    def get(self):
        try:
            ticker = request.args.get('ticker')
            if not ticker:
                return {"error": "Missing key parameter"}, 400
            
            response = dynamodb.get_item(
                TableName='Investify_DynamoDB',
                Key={'Ticker': {'S': ticker}}
            )
            
            if 'Item' in response:
                return response['Item'], 200
            else:
                return {"error": "Item not found"}, 404

        except (ClientError, ParamValidationError) as e:
            return {"error": str(e)}, 500

api.add_resource(GetItem, '/get_item')

if __name__ == '__main__':
    app.run(debug = True)
