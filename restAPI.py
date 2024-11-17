from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

api = Api(app)

#temporary stuff, likely will be replaced
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id='',
    aws_secret_access_key_id='',
    region_name='us-west-2',
)

table = dynamodb.Table('name')

class GetItem(Resource):

    def get(self):
        try:
            ticker = request.args.get('ticker')
            if not ticker:
                return {"error": "Missing key parameter"}, 400
            
            response = table.get_item(Key={'PrimaryKeyName': ticker})
            if 'Item' in response:
                return response['Item'], 200
            else:
                return {"error": "Item not found"}, 404

        except ClientError as e:
            return {"error": str(e)}, 500

class QueryItems(Resource):
    def get(self):
        try:
            attribute = request.args.get('attributes')
            if not attribute:
                return {"error": "Missing attribute parameter"}, 400
            response = table.query(
                IndexName="SecondaryIndexName",
                KeyConditionExpression="AttributeName = :val",
                ExpressionAttributeValues={":val": attribute},
            )
            return response.get('Items', []), 200
        except ClientError as e:
            return {"error": str(e)}, 500

api.add_resource(GetItem, '/get_item')
api.add_resource(QueryItems, '/query_items')

if __name__ == '__main__':
    app.run(debug = True)
