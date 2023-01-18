import os
import json
from azure.cosmos import CosmosClient, PartitionKey


ENDPOINT = os.environ["COSMOS_ENDPOINT"]
KEY = os.environ["COSMOS_KEY"]


def initiate(client):
    """ Initiate cosmos db/container/item"""
    database = client.create_database_if_not_exists(id="cosmicworks")
    partitionKeyPath = PartitionKey(path="/categoryId")
    container = database.create_container_if_not_exists(
        id="products", partition_key=partitionKeyPath, offer_throughput=400
    )

    newItem = {
        "id": "70b63682-b93a-4c77-aad2-65501347265f",
        "categoryId": "61dba35b-4f02-45c5-b648-c6badc0cbd79",
        "categoryName": "gear-surf-surfboards",
        "name": "Yamba Surfboard",
        "quantity": 12,
        "sale": False,
    }
    # container.create_item(newItem)

    return container
    # existingItem = container.read_item(
    #     item="70b63682-b93a-4c77-aad2-65501347265f",
    #     partition_key="61dba35b-4f02-45c5-b648-c6badc0cbd79",
    # )


def main():
    client = CosmosClient(url=ENDPOINT, credential=KEY)
    container = initiate(client)

    QUERY = """
        SELECT *
        FROM products p
        WHERE p.categoryId = @categoryId
    """
    CATEGORYID = "61dba35b-4f02-45c5-b648-c6badc0cbd79"
    params = [dict(name="@categoryId", value=CATEGORYID)]
    items = container.query_items(
        query=QUERY, parameters=params, enable_cross_partition_query=False
    )

    for item in items:
        print(json.dumps(item, indent=True))


if __name__ == "__main__":
    main()
