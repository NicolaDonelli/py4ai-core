py4ai core
====

[![PyPI](https://img.shields.io/pypi/v/py4ai-core.svg)](https://pypi.python.org/pypi/py4ai-core)
[![Python version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.python.org/pypi/py4ai-core)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://py4ai.github.io/py4ai-core/)
![Python package](https://github.com/NicolaDonelli/py4ai-core/workflows/CI%20-%20Build%20and%20Test/badge.svg)

--------------------------------------------------------------------------------


A Python library defining data structures optimized for machine learning pipelines 


## What is it ?
**py4ai-core** is a Python package with modular design that provides powerful abstractions to build data 
ingestion pipelines and run end to end machine learning pipelines. 
The library offers lightweight object-oriented interface to MongoDB as well as Pandas based data structures. 
The aim of the library is to provide extensive support for developing machine learning based applications 
with a focus on practicing clean code and modular design. 

## Features
Some cool features that we are proud to mention are: 

### Data layers 
1. Archiver: Offers an object-oriented design to perform ETL on Mongodb collections as well as Pandas DataFrames.
2. DAO: Data Access Object to allow archivers to serialize domain objects into the proper persistence layer support 
object (e.g. in the case of MongoDB, a DAO serializes a domain object into a MongoDB document) and to parse objects
retrieved from the given persistence layer in the correct representation in our framework (e.g. a text will be parsed in 
a Document while tabular data will be parsed in a pandas DataFrame).
3. Database: Object representing a relational database
4. Table: Object representing a table of a relational database

### Data Model
Offers the following data structures: 
1. Document : Data structure specifically designed to work with NLP applications that parses a json-like document 
into a couple of uuid and dictionary of information.
2. Sample : Data structure representing an observation (a.k.a. sample) as used in machine learning applications
3. MultiFeatureSample : Data structure representing an observation defined by a nested list of arrays.
4. Dataset : Data structure designed to be used specifically for machine learning applications representing a collection 
of samples.

## Installation
From pypi server
```
pip install py4ai-core
```

From source
```
git clone https://github.com/NicolaDonelli/py4ai-core
cd py4ai-core
make install
```

## Tests 
```
make tests
```

## Checks 
To run predefined checks (unit-tests, linting checks, formatting checks and static typing checks):
```
make checks
```

## Examples 

### Data Layers

The Data Layer abstractions are designed to decouple the business layers from 
the detail of the persistence layer implementation. The basic abstraction that will 
make this possible is the `Repository`.

As an example, imagine to have a domain business object `Entity`

```python
from pydantic import BaseModel

class Entity(BaseModel):
    my_id: int
    my_data: str
```

To start with, imagine we want to use csv files store on disk as a persistence 
layer. To do so, we will use the `CsvRepository` that uses pandas DataFrames stored
in memory and written to the disk as csv. Thus, we need to write the business logic
to serialize the `Entity` into a row of the pandas DataFrame, i.e. a pandas Series:

```python
import pandas as pd
from py4ai.core.data.layer.common.serialiazer import DataSerializer

class EntitySerializer(DataSerializer[int, int, Entity, pd.Series]):
    def to_object(self, entity: Entity) -> pd.Series:
        return pd.Series(entity.dict())

    def to_entity(self, document: pd.Series) -> Entity:
        return Entity(**document)

    def to_object_key(self, key: int) -> int:
        return key

    def get_key(self, entity: Entity) -> int:
        return entity.my_id
```

We can now instantiate the repository class that has all the methods for 
reading and writing objects from the persistence layer. 

```python
from py4ai.core.data.layer.pandas.repository import CsvRepository

repo = CsvRepository(filename, EntitySerializer())

entity = Entity(my_id=1234, my_data="Important data")

# This will create the entity in the persistence layer
await repo.create(entity)

# Retrieving the entity
retrieved = repo.retrieve(key=1234)

# Retrieving all entities
all_entities = repo.list()

```

Imagine now that, given the data increase in size, we now would like to change the 
persistence layer with a proper backend into something more structured and scalable, such 
as a NoSQL document-based data platform, such as MongoDB. We only need to create 
a new business logic to serialize/deserialize our class into a json (represented
in python by a dictionary):

```python
from bson import ObjectId
from py4ai.core.data.layer.mongo.serializer import create_mongo_id
from py4ai.core.data.layer.common.serialiazer import DataSerializer

class MongoDataSerializer(DataSerializer[int, ObjectId, Entity, dict]):
    def get_key(self, entity: Entity) -> int:
        return entity.my_id

    def to_object(self, entity: Entity) -> dict:
        doc = entity.dict()
        doc["_id"] = self.to_object_key(self.get_key(entity))
        return doc

    def to_entity(self, document: dict) -> Entity:
        return Entity(**document)

    def to_object_key(self, key: int) -> ObjectId:
        # This converts a string into an hash compatible with MongoDB format
        return create_mongo_id(str(key))
```

A new repository based on the MongoDB persistence layer can now be created using

```python
from py4ai.core.data.layer.mongo.repository import MongoRepository

repo = MongoRepository(collection, MongoDataSerializer())
```

This repository is compatible with the previous and can be used in place of the 
previous one, having the same signatures. 

#### Abstracting Data Querying 

The `Repository` abstraction also allow to retrieve data based on certain query/filters:

```python
entities = repo.retrieve_by_criteria(criteria)
```

However, the format of the query also depends on the type of the persistence layer and 
more specifically on how the data are organized. Therefore, in order to abstract
and decouple the notion of the underlying persistence layer, we need to define a general 
class containing the possible queries for a certain database:

```python
from typing import Generic
from abc import ABC, abstractmethod

from py4ai.core.data.layer.common.criteria import SearchCriteria

class EntityCriteriaFactory(ABC, Generic[Q]):
    @abstractmethod
    def by_id(self, id: int) -> SearchCriteria[Q]:
        ...
```

When considering a particular persistence layer, the querying business logic 
needs to be specified

```python
from py4ai.core.data.layer.mongo.criteria import MongoSearchCriteria

class MongoCriteriaFactory(EntityCriteriaFactory[Dict[str, Any]]):
    
    def by_id(self, my_id: int) -> MongoSearchCriteria:
        return MongoSearchCriteria({"my_id": my_id})

criteria = MongoCriteriaFactory()

entities = repo.retrieve_by_criteria(criteria.by_id(1234))
```

Note that `SearchCriteria` can be also joined using logical operators:

```python

entities = repo.retrieve_by_criteria(
    criteria.by_id(1234) & criteria.by_id(1235) 
)

entities = repo.retrieve_by_criteria(
    criteria.by_id(1234) | criteria.by_id(1235) 
)

```





### Data Model

Creating a PandasDataset object

```python
import pandas as pd
import numpy as np
from py4ai.core.data.model.ml import PandasDataset

dataset = PandasDataset(features=pd.concat([pd.Series([1, np.nan, 2, 3], name="feat1"),
                                            pd.Series([1, 2, 3, 4], name="feat2")], axis=1),
                        labels=pd.Series([0, 0, 0, 1], name="Label"))

# access features as a pandas dataframe 
print(dataset.features.head())
# access labels as pandas dataframe 
print(dataset.labels.head())
# access features as a python dictionary 
dataset.getFeaturesAs('dict')
# access features as numpy array 
dataset.getFeaturesAs('array')

# indexing operations 
# access features and labels at the given index as a pandas dataframe  
print(dataset.loc([2]).features.head())
print(dataset.loc([2]).labels.head())
```

Creating a PandasTimeIndexedDataset object

```python
import pandas as pd
import numpy as np
from py4ai.core.data.model.ml import PandasTimeIndexedDataset

dateStr = [str(x) for x in pd.date_range('2010-01-01', '2010-01-04')]
dataset = PandasTimeIndexedDataset(
    features=pd.concat([
        pd.Series([1, np.nan, 2, 3], index=dateStr, name="feat1"),
        pd.Series([1, 2, 3, 4], index=dateStr, name="feat2")
    ], axis=1))
```

## How to contribute ? 

We are very much willing to welcome any kind of contribution whether it is bug report, bug fixes, contributions to the 
existing codebase or improving the documentation. 

### Where to start ? 
Please look at the [Github issues tab](https://github.com/NicolaDonelli/py4ai-core/issues) to start working on open 
issues 

### Contributing to py4ai-core 
Please make sure the general guidelines for contributing to the code base are respected
1. [Fork](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) the py4ai-core repository. 
2. Create/choose an issue to work on in the [Github issues page](https://github.com/NicolaDonelli/py4ai-core/issues). 
3. [Create a new branch](https://docs.github.com/en/get-started/quickstart/github-flow) to work on the issue. 
4. Commit your changes and run the tests to make sure the changes do not break any test. 
5. Open a Pull Request on Github referencing the issue.
6. Once the PR is approved, the maintainers will merge it on the main branch.