# Dataframe cleaner

This project is base on [django-react-boilerplate] (https://github.com/vintasoftware/django-react-boilerplate)
It provide many useful configuraitons and setup that help speed up Django+React stack

## Main components of this project
- [**Django**] for Backend
- [**React**] for Frontend
- [**Wepack**] for bundling static assets
- [**Material-UI**] for useful UI component including table
  - It provides nice and user-friendly React UI component out of the box.
- [**Mongo**] for storing dataframe process metadata
  - This is to help speed up development process because of its flexible schema. However, longterm-wise it's better to make sure schema consistancy.
  - Note, At first **Djongo** library seems promise to have seemless integration with Django. However, this project is based on Django 5, and the latest version that Djongo support is only 4.2
- [**Minio**] for storing the dataframe file
  - It's a object storage that is compatible with Amazon S3.
  - It helps store object. In this project I store uploaded file to MINIO.

The Project Architecture 

<img width="755" alt="image" src="https://github.com/klurpicolo/dataframe-cleaner/assets/31367145/f47d98b5-e632-4721-b82f-4c01306df951">


## How to run project using Docker
prerequisites
- [**Make**] This help to easy setup by having a alias for useful commands
- [**Docker**] By using docker-compose, we can spin up all components easiy.

steps
- from the project root directory
- run `make docker_setup`
- run `make docker_up`
- go to localhost:9001 to access MINIO webpage
  - login with user `user` and password `password`
  - manually create a new bucket name `dataframes`

 <img width="815" alt="image" src="https://github.com/klurpicolo/dataframe-cleaner/assets/31367145/4da6ac6e-9183-4447-b2e6-5d93e6228ea5">
 
  - go to the newly created bucket and then set access policy to public
    
    <img width="729" alt="image" src="https://github.com/klurpicolo/dataframe-cleaner/assets/31367145/3136f36c-cc82-414c-98a5-357e8324b9dc">

- create a new mongo database name `dataframe_cleaner` with collection name `dataframe_metadata`

<img width="723" alt="image" src="https://github.com/klurpicolo/dataframe-cleaner/assets/31367145/2531bb75-2848-4e3d-b235-b264a817a212">

- Access [localhost:8000](http://localhost:8000/) Enjoy using Data Cleaner!!!


## Further suggestion for production use
This are the suggestion I have. I didn't do it due to the time constrain, and some of them are not require the this state of application yet.

- Feature
  - Extract Some constant such as category threshold to be parameters. So, user can set this value.
  - Add feature that allow user to rollback to a specific version, and allow them to process from a specific version.
  - Implement pagination on get dataframe API to enable users to see all data without loading csv.
  - Support User authentication and authorization.
  - Add detail explaination to UI about the decision process, so it's clear to users on what happend on each cell.

- Backend
  - Properly handle transaction across datasources.
  - Properly seperate app for processing dataframe, to enable properly isolate backend module.
  - Set up retention on MINIO to effectively manage disk space.
  - Seperate server that serve user request and processing data to enable proper scaling on load type (IO bound, or CPU bound)
  - For better user experience in case of processing large data file. We can consider to sent email to notify end users when data is processed.

- Frontend
  - Use TypeScript instead of Javascript to support typing. This'll improve code type consistancy in long term.
  - Use Redux to properly manage Frontend state. This version just focus on protopying, so I only use React to control state.

- Test
  - Add postman test script
  - Add integration test on backend and frontend
  - Do load testing on dataframe processing
