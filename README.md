# credentialleakDB

A database structure to store leaked credentials. 

Think: our own, internal HaveIBeenPwned database.

## Why?

1. To quickly find duplicates before sending it on to further process the data
2. To have a way to load diverse credential breaches into a common structure and do common queries on it
3. To quickly generate statistics on credential leaks
4. To have a well defined interface to pass on data to pass it on to other automation steps

## Documentation

See the [confluence page](https://conf.s.cec.eu.int/display/~kaplale/CredentialLeakDB) for a high level description.

SQL structure: [db.sql](db.sql)

