import boto3
import json
import os

# Use environment variables or IAM roles for credentials
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def delete_all_items(table, primary_key):
    try:
        scan = table.scan()
        with table.batch_writer() as batch:
            for each in scan['Items']:
                batch.delete_item(
                    Key={
                        primary_key: each[primary_key]
                    }
                )
    except Exception as e:
        print(f"Error deleting items from {table.name}: {e}")

def restore_dynamodb_tables():
    table_configs = [
        {"table_name": "blog-users", "primary_key": "email"},
        {"table_name": "blog-posts", "primary_key": "id"}
    ]

    for config in table_configs:
        try:
            table = dynamodb.Table(config["table_name"])

            # Check if the table exists
            if not table.creation_date_time:
                print(f"Table {config['table_name']} does not exist.")
                continue

            # Get the directory of the script
            script_directory = os.path.dirname(os.path.abspath(__file__))

            # Delete all existing items in the table
            delete_all_items(table, config["primary_key"])

            # Restore from JSON file in the ./dynamoDB-refresh directory
            file_path = os.path.join(script_directory, 'dynamoDB-refresh', f'{config["table_name"]}.json')
            with open(file_path) as db_file_json:
                db_file = json.load(db_file_json)

            for db_item in db_file:
                table.put_item(Item=db_item)

            print(f"{config['table_name']} table restored")
        except Exception as e:
            print(f"Error restoring {config['table_name']} table: {e}")

if __name__ == "__main__":
    restore_dynamodb_tables()
