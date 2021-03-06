# Pulling Data Out of Oracle database with Python using SQLAlchemy and Unit of Work Design Pattern

In this tutorial style article we are going to provide you with some steps to connect to an Oracle database in a Python application by using SQLAlchemy ORM (Object relational mapping) and the Unit of Work Design Pattern. By the end of it you will be able to perform queries using raw SQL commands.

## Introduction 

Oracle is one of the most popular databases out there, it's used by companies like JPMorgan Chase, IBM, ABN Amro, Wells Fargo and so on. Considering this, there are good chances that one day you might bump into it in your ephemeral lifetime as a software developer. 

It can be pretty daunting to have to use repetitive SQL commands to search for specific information in databases, right? For simple and quick tasks it's fine to use a software like Oracle SQL Developer to perform your queries, but if you are working on a specific application with more complicated business rules, then you might want to condense those repetitive SQL commands in a method, for example. If you are writing an application in Python which might need to query an Oracle database, follow me through the next steps to check out my approach to this.

## Case Scenario

Let's suppose you work for a financial institution and you are given a task to create Financial Audit Reports for a certain quarter of the year or month. These reports would provide detailed information about macroeconomic variables, mortgage rates and so on.

This is an important task because in the end these reports are going to be evaluated by an Auditing company, like EY or PwC, in order to make sure that the financial records are a fair and accurate representation of the transactions your company claim to represent.

The business analysts in your team usually work on these reports, many of them are already savvy about SQL commands and perform them using the Oracle SQL Developer software. But they don't want spend infinite boring hours performing repetitive queries and populating the results on excel sheets, so they ask your help to automate this process. After all, we are in the 21st century already and life is too short to repeat themselves every month or quarter. Plus, sometimes little mistakes are made here and there... damn humans. 

So, basically they would provide you with the queries they usually perform to gather the report data and you would adapt them according to the variant parameters, for example, year, month, quarter, statuses of workflows etc.


## Why use SQLAlchemy?

SQLAlchemy is a library used to interact with a wide variety of databases such as Postgres, MySQL, SQLite, Oracle, and many others. It enables you to create data models and queries in a manner that feels like normal Python classes and statements. It's considered by many the main way of working with relational databases in Python. 

(The top reason to use SQLAlchemy is to abstract your code away from the underlying database and its associated SQL peculiarities. SQLAlchemy leverages powerful common statements and types to ensure its SQL statements are crafted efficiently and properly for each database type and vendor without you having to think about it. This makes it easy to migrate logic from Oracle to PostgreSQL or from an application database to a data warehouse. It also helps ensure that database input is sanitized and properly escaped prior to being submitted to the database. This prevents common issues like SQL injection attacks.)[1]

I hope you find it interesting so far. Now let's get our hands a bit dirty.

## Step 1: Creating a Python Environment and Installing Python Libraries

In this section we are going to create a virtual environment to install our dependencies. This avoids us to install our packages into a global Python environment.

Create a folder for your project and in that folder use the following commands according to your operational system.
In the example below ".env" is the name of the environment, feel free to name you virtual environment with whichever name you want.

```bash
# macOS/Linux
sudo apt-get install python3-venv  # If needed
python3 -m venv env

# Windows
python -m venv env
```

Activate the virtual environment:

```bash
#(Linux/macOS)
source env/bin/activate 

#Windows)
env\scripts\activate 
```

You know the environment is activated when the command prompt shows **(env)** at the beginning.

The python libraries we need to connect to an Oracle database are essentially `cx_Oracle` and `sqlalchemy`, let's place them in our requirements.txt file in the root folder of our project:

*requirements.txt*
```bash
# These libraries are required to run the script
cx_Oracle
sqlalchemy
python-dotenv
```

To install the packages, you can just run:

`pip install -r requirements.txt`

If you would like to install them individually, just do:

`pip install <somepackage>`

## Step 2: Installing Database Drivers

(By default, SQLAlchemy will support SQLite3 with no additional drivers; however, an additional database driver that uses the standard Python DBAPI (PEP-249) specification is needed to connect to other databases. These DBAPIs provide the basis for the dialect each database server speaks and often enable the unique features seen in different database servers and versions.)[1]

[cx_Oracle](https://docs.sqlalchemy.org/en/14/dialects/oracle.html#module-sqlalchemy.dialects.oracle.cx_oracle) is one dialect(DBAPI) option available which adds support for the Oracle database.
All you have to do is go to the cx_Oracle [official webpage](https://oracle.github.io/python-cx_Oracle/) download and install the proper driver according to your operational system. 

## Step 3: Test Your Database Connection Credentials Before Start Coding

Make sure you have all the necessary information to connect to your database. A connection string provides information about:

* Database type (Postgres, MySQL, Oracle etc.)  
* Dialect (Psycopg2, PyMySQL, cx_Oracle etc.)  
* Location of the database (file or hostname of the database server)
* Authentication details (username and password) [optional] 
* Database server port [Optional]
* Database name [optional]

If you have the Oracle SQL Developer software installed in your machine you can test your connection by providing this information through a manual connection. 
![Oracle SQL Developer](../images/oracle_sql_developer.jpg "Oracle SQL Developer]")

If after that you are able to successfully connect to the database and see the schemas and tables you are interested in, then you are good to go to the next steps.

## Step 4: Creating a ".env" File to Store Information About Your Database Connection

It's a good practice to create a `.env` file to store sensitive information about your project. This way, your application will become less vulnerable to malicious attacks. Each developer involved in the creation of the project should create their own `.env` file in which they will place their credentials to the database, see template below.

*.env*
```
export PYTHONPATH="~/<project_path>"

export DB_HOST=<your_db_hostname>
export DB_USER=<your_db_hostname>
export DB_SERVICE=<your_db_service_name>
export DB_PASSWORD=<your_db_password>
export DB_PORT=<your_db_port>
```

Usually this file is placed in the the root folder of our project.

## Step 5: Reading Configuration Information from Environment Variable

Now let's create a `config.py` file to read our database credentials. For this we are going to use a Python library called [`python-dotenv`](https://pypi.org/project/python-dotenv/), which we already added in our `requirements.txt` file. `python-dotenv` reads the key-value pair from `.env` file and adds them to the environment variable.

*src/config.py*
```python
import pathlib
from os import environ, path
 
from dotenv import load_dotenv
 
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()
 
load_dotenv(path.join(PROJECT_ROOT, ".env"))
 
 
def get_oracle_db_uri() -> str:
   """
   Load database environment variables from .env
   :return: string db connection
   """
   host = environ.get("DB_HOST")
   user = environ.get("DB_USER")
   password = environ.get("DB_PASSWORD")
   service_name = environ.get("DB_SERVICE")
   port = environ.get("DB_PORT")
   return f"oracle+cx_oracle://{user}:{password}@{host}:{port}/{service_name}"
```

Note the connection string format returned in the method above:

```bash
oracle+cx_oracle://user:pass@host:port/dbname[?key=value&key=value...]
```

## Step 6: Connecting to the Database

Now that we have our Python dependencies and DBAPI installed, let’s actually build an engine to connect to a database.

The [SQLAlchemy engine](https://docs.sqlalchemy.org/en/14/core/engines.html) creates an interface to the database to execute SQL statements. This enables our Python code not to worry about the differences between databases or DBAPIs. Creating an engine is just a matter of issuing a single call:

```python
from sqlalchemy import create_engine

create_engine(get_oracle_db_uri(), max_identifier_length=128, pool_timeout=30
```

### The Unit of Work Design Pattern

You can change the database with each change to your object model, but this can lead to lots of very small database calls, adding latency to your system, mainly if a lot of communication happens across the layers of your infrastructure.

(While performing CRUD operations you can use the Unit of Work (UoW, which we pronounce “you-wow”) to check for inconsistencies by verifying that none of the objects changed on the database during the business transaction. When it comes time to commit, it figures out everything that needs to be done to alter the database as a result of your work. It opens a transaction, does any concurrency checking and writes changes out to the database.)[2] 

In addition, the Unit of Work allows us to decouple our service layer from the data layer. If you would like to get a deeper dive into The Unit of Work design pattern applied to a Python project, I recommend you to read the chapter 6 of the book [Enterprise Architecture Patterns With Python](https://www.cosmicpython.com/book/chapter_06_uow.html) written by [Harry Percival](https://twitter.com/hjwp). The code bellow is an adaptation of what he presented in his book.


*data_access_layer/unit_of_work.py*
```python
import abc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from src import config


class AbstractUnitOfWork(abc.ABC):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_oracle_db_uri(), max_identifier_length=128, pool_timeout=30
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

```


The UoW acts as a single entry point to our persistence storage and keeps track of what objects were loaded. This gives us three useful things: 

* A stable snapshot of the database to work with, so the objects we use aren’t changing halfway through an operation
* A way to persist all of our changes at once, so if something goes wrong, we don’t end up in an inconsistent state
* A simple API to our persistence concerns and a handy place to get a repository[3]


## Step 7: Encapsulating your Queries in Service Methods

Now that we set up an engine to communicate with the database we are ready to perform our query commands.

Let's create a service to get information about a fictitious `workflow` entity present in our database:


*src/automation/service_layer/workflows.py*

```python
from src.automation.data_access_layer import unit_of_work


def get_workflows_by_status(status: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = list(uow.session.execute(
            'SELECT * FROM X_OWNER.workflows WHERE status = :status',
            status=status
        ))
    return [dict(r) for r in results]
```

Which might return a list of dictionaries like this:

```json
[
    {
      "id": 34547,
      "calculation_id": 9616,
      "workflow_id": 3,
      "status": "REFR_APPROVE"
    },
    {
      "id": 34557,
      "calculation_id": 9616,
      "workflow_id": 4,
      "status": "REFR_APPROVE"
    },
    {
      "id": 34567,
      "calculation_id": 9616,
      "workflow_id": 5,
      "status": "REFR_APPROVE"
    },
    ...
```

In which each key is correspondent to the column property of the entity `workflows`.

## Step 8: The Main Application

Now you can consume the small previous service method we worked on in you main application. Here we have a simple main script. But you could consume your service each way you like or needed, for example, you could use in a Django or Flask application, in your Jupyter notebook and so on.

*src/main.py*

```python
from src.automation.service_layer import get_workflows_by_status

class AutomationFramework:
    def __init__(self, status):
        self.status = status
        
    def run(self):
        get_workflows_by_status(self.status)

if __name__ == "__main__":
    automation = AutomationFramework("FINISHED")
    automation.run()
```

## General Architecture of the System

The unit of work is going to be initialized in the main application, which invokes the services, which collaborates with the UoW.

![General Architecture of the System](../images/architecture_flowchart.jpg "General Architecture of the System")


## Resources

[1] Copeland, R. (2008). Essential SQLAlchemy. Sebastopol, CA: O’Reilly Media. 

[2] Fowler, M. (2002). Patterns of Enterprise Application Architecture. Boston, MA: Addison-Wesley Educational. 

[3] PERCIVAL, HARRY. ENTERPRISE ARCHITECTURE PATTERNS WITH PYTHON: O'REILLY MEDIA, 2020. 

[4] https://docs.sqlalchemy.org/en/14/dialects/oracle.html 

[5] https://oracle.github.io/python-cx_Oracle/

[6] https://docs.sqlalchemy.org/en/14/dialects/oracle.html

[7]:[Flask Tutorial in Visual Studio Code](https://code.visualstudio.com/docs/python/tutorial-flask)




