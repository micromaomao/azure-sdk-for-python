# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""
FILE: schema_registry.py
DESCRIPTION:
    This sample demonstrates authenticating the SchemaRegistryClient and basic usage, including:
        - registering a schema.
        - getting a schema by its ID.
        - getting a schema by its version.
        - getting schema id.
USAGE:
    python schema_registry.py
    Set the environment variables with your own values before running the sample:
    1) SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    2) SCHEMAREGISTRY_GROUP - The name of the schema group.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see
 https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import os
import json

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient, SchemaFormat


SCHEMAREGISTRY_FQN = os.environ["SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE"]
GROUP_NAME = os.environ["SCHEMAREGISTRY_GROUP"]
NAME = "your-schema-name"
FORMAT = SchemaFormat.AVRO

SCHEMA_JSON = {
    "namespace": "example.avro",
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "favorite_number", "type": ["int", "null"]},
        {"name": "favorite_color", "type": ["string", "null"]},
    ],
}
NEW_SCHEMA_JSON = {
    "namespace": "example.avro",
    "type": "record",
    "name": "User2",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "favorite_number", "type": ["int", "null"]},
        {"name": "favorite_color", "type": ["string", "null"]},
    ],
}
DEFINITION = json.dumps(SCHEMA_JSON, separators=(",", ":"))
NEW_DEFINITION = json.dumps(NEW_SCHEMA_JSON, separators=(",", ":"))


def register_schema(client, group_name, name, definition, format):
    print("Registering schema...")
    schema_properties = client.register_schema(group_name, name, definition, format)
    print(f"Schema registered, returned schema id is {schema_properties.id}")
    print(f"Schema properties are {schema_properties}")
    return schema_properties


def get_schema_by_id(client, schema_id):
    print("Getting schema by id...")
    schema = client.get_schema(schema_id)
    print(f"The schema string of schema id: {schema_id} is {schema.definition}")
    print(f"Schema properties are {schema.properties}")
    return schema.definition


def get_schema_by_version(client, group_name, name, version):
    print("Getting schema by version...")
    schema = client.get_schema(group_name=group_name, name=name, version=version)
    print(
        f"The schema string of schema id: {schema.properties.id} is {schema.definition}"
    )
    print(f"Schema properties are {schema.properties}")
    return schema.definition


def get_old_schema_by_version(client, group_name, name, new_definition):
    updated_schema_properties = client.register_schema(
        group_name, name, new_definition, FORMAT
    )
    print(f"Registered new schema of version: {updated_schema_properties.version}")
    old_version = updated_schema_properties.version - 1
    schema = client.get_schema(group_name=group_name, name=name, version=old_version)
    print(f"Retrieving old schema v{schema.properties.version}: {schema.definition}")
    return schema.definition


def get_schema_id(client, group_name, name, definition, format):
    print("Getting schema id...")
    schema_properties = client.get_schema_properties(
        group_name, name, definition, format
    )
    print(f"The schema id is: {schema_properties.id}")
    print(f"Schema properties are {schema_properties}")
    return schema_properties.id


if __name__ == "__main__":
    token_credential = DefaultAzureCredential()
    schema_registry_client = SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FQN, credential=token_credential
    )
    with schema_registry_client:
        schema_properties = register_schema(
            schema_registry_client, GROUP_NAME, NAME, DEFINITION, FORMAT
        )
        schema_str = get_schema_by_id(schema_registry_client, schema_properties.id)
        schema_str = get_schema_by_version(
            schema_registry_client, GROUP_NAME, NAME, schema_properties.version
        )
        schema_str = get_old_schema_by_version(
            schema_registry_client, GROUP_NAME, NAME, NEW_DEFINITION
        )
        schema_id = get_schema_id(
            schema_registry_client, GROUP_NAME, NAME, DEFINITION, FORMAT
        )
