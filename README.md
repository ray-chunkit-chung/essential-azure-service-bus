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
az deployment group create--subscription $SUBSCRIPTION \
                           --resource-group $RESOURCE_GROUP \
                           --name rollout01 \
                           --template-file ARMTemplate/ServiceBus/template.json \
                           --parameters ARMTemplate/ServiceBus/parameters.json
# Check servicebus properties
# az servicebus namespace show --name $SERVICEBUS_NAMESPACE --resource-group $RESOURCE_GROUP
# az servicebus queue show --name $SERVICEBUS_QUEUE --resource-group $RESOURCE_GROUP --namespace-name $SERVICEBUS_NAMESPACE
# az servicebus topic show --name $SERVICEBUS_TOPIC --resource-group $RESOURCE_GROUP --namespace-name $SERVICEBUS_NAMESPACE
```

## Step 3 Install azure sdk for python for demo example

```bash
sudo apt-get install -y python3 python3-dev
sudo ln -sf /usr/bin/python3 /usr/bin/python
export PYTHONPATH=/usr/bin/python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py
sudo pip install azure-servicebus
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

Send message

```bash
source .env
python example/send_message_queue.py 
```

Receive message

```bash
source .env
python example/receive_message_queue.py 
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
