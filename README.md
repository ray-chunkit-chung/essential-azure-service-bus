# azure-service-bus

add an Azure service bus

<https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-resource-manager-namespace-queue>

<https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-resource-manager-namespace-topic>

<https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-topics-subscriptions>

## Step 1 Login azure

Set app variables by saving in .env file

```bash
export SUBSCRIPTION="xxx"
export TENANT="xxx"
export LOCATION="eastus"
export RESOURCE_GROUP="xxx"
export STORAGE_ACCOUNT="xxx"
export SKU_STORAGE="Standard_LRS"
```

Install azure cli & login

```bash
source .env
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login --tenant $TENANT
az account set -s $SUBSCRIPTION
```

## Step 2 Deploy azure service bus

```bash
source .env
az group create --subscription $SUBSCRIPTION \
                --name $RESOURCE_GROUP \
                --location $LOCATION
az deployment group create --subscription $SUBSCRIPTION \
                           --resource-group $RESOURCE_GROUP \
                           --name rollout01 \
                           --template-file ARMTemplate/ServiceBus/template.json \
                           --parameters ARMTemplate/ServiceBus/parameters.json
```

Check if service bus deploys successfully

```bash
az servicebus namespace show --name $SERVICEBUS_NAMESPACE --resource-group $RESOURCE_GROUP
az servicebus queue show --name $SERVICEBUS_QUEUE --resource-group $RESOURCE_GROUP --namespace-name $SERVICEBUS_NAMESPACE
az servicebus topic show --name $SERVICEBUS_TOPIC --resource-group $RESOURCE_GROUP --namespace-name $SERVICEBUS_NAMESPACE
```

## Step 3 Install azure sdk for python for demo example

```bash
sudo apt-get install -y python3 python3-dev python3-venv
python3 -m venv .venv
source .venv/bin/activate
# sudo ln -sf /usr/bin/python3 /usr/bin/python
# export PYTHONPATH=/usr/bin/python
# curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# sudo python get-pip.py
pip install --upgrade -r requirements.txt
```

Check if install successful

```python
from azure.servicebus import ServiceBusClient, ServiceBusMessage
```

## Step 4 Try send and receive messages

On service bus deployment, default authorization-rule keys with Name=RootManageSharedAccessKey are generated. We need the key to send & receive messages used in python script

```bash
export PRIMARY_CONNECTION_STRING="$(az servicebus namespace authorization-rule keys list --resource-group $RESOURCE_GROUP --namespace-name $SERVICEBUS_NAMESPACE --name RootManageSharedAccessKey | jq '.primaryConnectionString' | tr -d '"')"
export SECONDARY_CONNECTION_STRING="$(az servicebus namespace authorization-rule keys list --resource-group $RESOURCE_GROUP --namespace-name $SERVICEBUS_NAMESPACE --name RootManageSharedAccessKey | jq '.secondaryConnectionString' | tr -d '"')"
```

Send/receive message to/from queue

```bash
source .env
python example/send_message_queue.py 
python example/receive_message_queue.py 
```

Send/receive message to/from topic

```bash
source .env
python example/send_receive_message_topic.py
```

## Finally Delete resources

After experiment, delete all resources to avoid charging a lot of money

```bash
source .env
az group delete -y --name $RESOURCE_GROUP
```

There can be some managed resources to delete. Check them by

```bash
az group list --subscription $SUBSCRIPTION
```

Delete them by

```bash
source .env
az group delete --name $(az group list --subscription $SUBSCRIPTION | jq '.[].name' | tr -d '"')
```

## Bonus A Messaging with cosmos db via logic app  

Connection between logic app and cosmos
<https://learn.microsoft.com/en-us/azure/connectors/connectors-create-api-cosmos-db?tabs=standard>

### Step A1 Create a comos db

```bash
source .env
az group create --name $RESOURCE_GROUP \
                --location $LOCATION
az cosmosdb create \
    --resource-group $RESOURCE_GROUP \
    --name $COSMOS_NAME \
    --locations regionName=$LOCATION
export COSMOS_CONNECTION_STRING="$(az cosmosdb keys list \
        --type connection-strings \
        --resource-group $RESOURCE_GROUP \
        --name $COSMOS_NAME \
    | jq '.connectionStrings[0].connectionString' \
    | tr -d '"')"
export COSMOS_ENDPOINT="$(az cosmosdb show \
        --resource-group $RESOURCE_GROUP \
        --name $COSMOS_NAME \
        --query "documentEndpoint" \
    | tr -d '"')"
export COSMOS_KEY="$(az cosmosdb keys list \0
        --resource-group $RESOURCE_GROUP \
        --name $COSMOS_NAME \
    | jq '.primaryMasterKey' \
    | tr -d '"')"
```

```bash
sudo apt-get install -y python3 python3-dev python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade -r requirements.txt
python example/run_sql_cosmos.py
```

```bash
az deployment group create --subscription $SUBSCRIPTION \
                           --resource-group $RESOURCE_GROUP \
                           --name rollout01 \
                           --template-file ARMTemplate/LogicAppStandard/template.json \
                           --parameters ARMTemplate/LogicAppStandard/parameters.json
```

## Bonus B  SQL CDC

Service b
<https://stackoverflow.com/questions/69319332/azure-service-bus-post-to-a-queue-and-a-topic-inside-transaction-scope>

SQL CDC with Kafka
<https://hevodata.com/learn/kafka-cdc-sql-server/#m1>

SQL CDC with Event Hub
<https://www.sqlservercentral.com/blogs/streaming-etl-sql-change-data-capture-cdc-to-azure-event-hub-2>
<https://github.com/rolftesmer/SQLCDC2EventHub>
<https://www.sqlservercentral.com/blogs/streaming-etl-sql-change-data-capture-cdc-to-azure-event-hub>
