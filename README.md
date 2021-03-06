# credentialleakDB

[![Pylint](https://github.com/EC-DIGIT-CSIRC/credentialLeakDB/actions/workflows/pylint.yml/badge.svg)](https://github.com/EC-DIGIT-CSIRC/credentialLeakDB/actions/workflows/pylint.yml)
[![flak8 and pytest](https://github.com/EC-DIGIT-CSIRC/credentialLeakDB/actions/workflows/python-app.yml/badge.svg)](https://github.com/EC-DIGIT-CSIRC/credentialLeakDB/actions/workflows/python-app.yml)
[![CodeQL](https://github.com/EC-DIGIT-CSIRC/credentialLeakDB/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/EC-DIGIT-CSIRC/credentialLeakDB/actions/workflows/codeql-analysis.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=digits2_credentialLeakDB&metric=alert_status&token=cee9c8232570fa1000ab4770feb571fd3e85ff39)](https://sonarcloud.io/dashboard?id=digits2_credentialLeakDB)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=digits2_credentialLeakDB&metric=sqale_rating&token=cee9c8232570fa1000ab4770feb571fd3e85ff39)](https://sonarcloud.io/dashboard?id=digits2_credentialLeakDB)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=digits2_credentialLeakDB&metric=reliability_rating&token=cee9c8232570fa1000ab4770feb571fd3e85ff39)](https://sonarcloud.io/dashboard?id=digits2_credentialLeakDB)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=digits2_credentialLeakDB&metric=security_rating&token=cee9c8232570fa1000ab4770feb571fd3e85ff39)](https://sonarcloud.io/dashboard?id=digits2_credentialLeakDB)
[![codecov](https://codecov.io/gh/EC-DIGIT-CSIRC/credentialLeakDB/branch/main/graph/badge.svg?token=SS5F8EXQON)](https://codecov.io/gh/EC-DIGIT-CSIRC/credentialLeakDB)


A database structure to store leaked credentials. 

Think: our own, internal [HaveIBeenPwned](https://haveibeenpwned.com/) database.

## Why?

1. To quickly find duplicates before sending it on to further process the data
2. To have a way to load diverse credential breaches into a common structure and do common queries on it
3. To quickly generate statistics on credential leaks
4. To have a well defined interface to pass on data to pass it on to other automation steps

## Documentation

### Installation

#### Docker

#### Via pip and venv

```bash
git clone https://github.com/EC-DIGIT-CSIRC/credentialLeakDB.git
cd credentialLeakDB
# create a virtualenv
virtualenv --python=python3.7 venv
source venv/bin/activate
pip install -r requirements.txt
```

Next, make sure the following files exist:
  * ``VIPs.txt`` ... a \n separated list of email addresses which you would consider VIPs.
  * api/config.py ... see below
 
### Database structure
Search in Confluence for "credentialLeakDB" in the Automation space.

SQL structure: [db.sql](db.sql)

The EER diagram __intentionally__ got simplified a lot. If we are going to store billions of repeated ``text`` datatype records, we can 
go back to more normalization. For now, however, this seems to be enough.


![EER Diagram](EER.png)



### Meaning of the fields

#### Table ``leak``

|      Column       |           Type           | Collation | Nullable |  Description          |                                          
|------------------ | ------------------------ | --------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| ``id``                | integer                  |           | not null | _primary key. Auto-generated_. |
| ``breach_ts``         | timestamp with time zone |           |          | If known, the timestamp when the breach happened. |
| ``source_publish_ts`` | timestamp with time zone |           |          | The timestamp according when the source (f.ex. Spycloud) published the data. |
| ``ingestion_ts``      | timestamp with time zone |           | not null | The timestamp when we ingested the data. |
| ``summary``           | text                     |           | not null | A short summary (slug) of the leak. Used for displaying it somewhere |
| ``ticket_id``         | text                     |           |          |  |
| ``reporter_name``     | text                     |           |          | The name of the reporter where we got the notification from. E.g. CERT-eu, Spycloud, etc... Who sent us the data? |
| ``source_name``       | text                     |           |          | The name of the source where this leak came from. Either the name of a collection or some other name. |

```
Indexes:
    "leak_pkey" PRIMARY KEY, btree (id)
Referenced by:
    TABLE "leak_data" CONSTRAINT "leak_data_leak_id_fkey" FOREIGN KEY (leak_id) REFERENCES leak(id)
 ```
 
 #### Table ``leak_data``
                                                                                                                    
|        Column        |  Type   | Collation | Nullable |  Description                                                             
--------------------- | ------- | --------- | -------- | -----------------------------------------------------------------------------------------------------------------------------------
 ``id``                   | integer |           | not null | _primary key, auto-generated_. | 
 ``leak_id``              | integer |           | not null | references a ``leak(id)`` | 
 ``email``                | text    |           | not null | The email address associated with the leak. | 
 ``password``             | text    |           | not null | Either the encrypted or unencrypted password. If the unencrypted password is available, that is what is going to be in this field. |
 ``password_plain``       | text    |           |          | The plaintext password, if known. |
 ``password_hashed``      | text    |           |          | The hashed password, if known. |
 ``hash_algo``            | text    |           |          | If we can determine the hashing algo and the password_hashed field is set, for example "md5" or "sha1" |
 ``ticket_id``            | text    |           |          | References the ticket systems' ticket ID associated with handling this credential leak . This ticket could contain infos on how we contacted the affected user. | 
 ``email_verified``       | boolean |           |          | If the email address was verified if it does exist and is active | 
 ``password_verified_ok`` | boolean |           |          | Was that password still valid / active? | 
 ``ip``                   | inet    |           |          | IP address of the client PC in case of a password stealer. | 
 ``domain``               | text    |           |          | Domain address of the user's email address. | 
 ``browser``              | text    |           |          | If the password was leaked via a password stealer malware, then the browser of the user goes here. Otherwise empty. | 
 ``malware_name``         | text    |           |          | If the password was leaked via a password stealer malware, then the malware name goes here. Otherwise empty. |
 ``infected_machine``     | text    |           |          | If the password was leaked via a password stealer malware, then the infected (Windows) PC name (some ID for the machine) goes here. |
 ``dg``                   | text    |           | not null | The affected DG (in other organisations, this would be called "department")
 ``count_seen``           | integer |           |          | How often did we already see this unique combination (leak, email, password, domain). I.e. this is a duplicate counter.  | 

```
Indexes:
    "leak_data_pkey" PRIMARY KEY, btree (id)
    "constr_unique_leak_data_leak_id_email_password_domain" UNIQUE CONSTRAINT, btree (leak_id, email, password, domain)
    "idx_leak_data_unique_leak_id_email_password_domain" UNIQUE, btree (leak_id, email, password, domain)
    "idx_leak_data_dg" btree (dg)
    "idx_leak_data_email" btree (upper(email))
    "idx_leak_data_email_password_machine" btree (email, password, infected_machine)
    "idx_leak_data_malware_name" btree (malware_name)
Foreign-key constraints:
    "leak_data_leak_id_fkey" FOREIGN KEY (leak_id) REFERENCES leak(id)
```    


# Usage of the API

Here is how to use the API endpoints: you can start the server (follow the instructions below) and go to ``$servername/docs`` where $servername is of course the domain / IP address you installed it under. The ``docs/`` endpoint hosts a swagger / OpenAPI 3 

## GET parameters

These are pretty self-explanatory thanks to the swagger UI.

## POST and PUT

For HTTP POST (a.k.a INSERT into DB) you will need to provide the following JSON info:

### leak object
```json
{
  "id": 0,
  "ticket_id": "string",
  "summary": "string",
  "reporter_name": "string",
  "source_name": "string",
  "breach_ts": "2021-03-29T12:21:56.370Z",
  "source_publish_ts": "2021-03-29T12:21:56.370Z"
}

```

The ``id`` field *only* needs to be filled out when PUTing data there (a.k.a UPDATE statement). Otherwise please leave it out when POSTing a new leak_data row.
The id is the internal automatically generated primary key (ID) and will be assigned. So when you use the ``HTTP POST /leak`` endpoint, please leave out ``id``. The answer will be a JSON array with a dict with the id inside, such as:

```json
{
  "meta": {
    "version": "0.5",
    "duration": 0.006,
    "count": 1
  },
  "data": [
    {
      "id": 18
    }
  ],
  "error": null
}
```

Meaning: the version of the API was 0.5, the query duration was 0.006 sec (6 millisec), one answer. The ``data`` array contains one element: id=18. Meaning, the ID of the inserted leak object was 18. You can now reference this in the leak_data object insertion.

### leak_data object

Same as the leak object, here the ``id`` field *only* needs to be filled out when PUTing data there (a.k.a UPDATE statement). Otherwise please leave it out when POSTing a new leak_data row. **Note well**: the leak_id field needs to be filled out in this case. You **first** have to create leak object and then afterwards the leak_data object.

```json
{
  "id": 0,
  "leak_id": 0,
  "email": "user@example.com",
  "password": "string",
  "password_plain": "string",
  "password_hashed": "string",
  "hash_algo": "string",
  "ticket_id": "string",
  "email_verified": true,
  "password_verified_ok": true,
  "ip": "string",
  "domain": "string",
  "browser": "string",
  "malware_name": "string",
  "infected_machine": "string",
  "dg": "string"
}
```

## ``import/csv/`` endpoint

Also pretty self-explanatory. You need to first create a leak object, give it's ID as a GET-style parameter and upload the CSV in spycloud format via the Form.


## Installation

1. Install git and checkout this repository:
```bash
apt install git
git clone ...
cd credentialLeakDB
```

3. Install Postgresql:
```bash 
# in Ubuntu:
apt install postgresql-12           
# alternatively, if you are in Debian 10, you can also use postgresql-11, both work:
# apt install postgresql-11
```

2. as user postgres:
```bash
sudo su - postgres
createdb credentialleakdb
createuser credentialleakdb
psql -c "ALTER ROLE credentialleakdb WITH PASSWORD '<insert some random password here>'" template1
```

3. create the DB:
```psql -u credentialleakdb credentialleakdb < db.sql```

5. set the env vars: 
```bash
export PORT=8080
export DBNAME=credentialleakdb
export DBUSER=credentialleakdb
export DBPASSWORD=... <insert the password you gave the user> ...
export DBHOST=localhost
```
5. Create a virtual environment if it does not exist yet:
   ```bash
   virtualenv --python=python3.7 venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. start the program from the main directory:
```bash
export PYTHONPATH=$(pwd); uvicorn --reload --host 0.0.0.0 --port $PORT api.main:app
```

## Configuration.

Please copy the file ``config.SAMPLE.py`` to ``api/config.py`` and adjust accordingly.
Here you can set API keys etc.



