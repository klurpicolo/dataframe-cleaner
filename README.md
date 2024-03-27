# Dataframe Cleaner

This project is based on [django-react-boilerplate](https://github.com/vintasoftware/django-react-boilerplate), offering various configurations and setups to expedite Django+React stack development.

## Main Components

- **Django**: Backend framework
- **React**: Frontend library
- **Webpack**: Bundler for static assets
- **Material-UI**: Provides useful UI components, including tables
- **Mongo**: Stores dataframe process metadata, offering flexibility in schema (Note: Ensure long-term schema consistency)
- **Minio**: Object storage compatible with Amazon S3, used for storing dataframe files

### Project Architecture
![Project Architecture](https://github.com/klurpicolo/dataframe-cleaner/assets/31367145/f47d98b5-e632-4721-b82f-4c01306df951)

## Running the Project with Docker

### Prerequisites
- **Make**: Simplifies setup with useful command aliases
- **Docker**: Allows easy deployment via docker-compose

### Steps
1. Navigate to the project root directory.
2. Run `make docker_setup`.
3. Run `make docker_up`.
4. Access MINIO webpage at [localhost:9001](http://localhost:9001/).
   - Login with credentials: user/password.
   - Manually create a new bucket named `dataframes`.
   ![MINIO Webpage](https://github.com/klurpicolo/dataframe-cleaner/assets/31367145/4da6ac6e-9183-4447-b2e6-5d93e6228ea5)
   - Set access policy to public for the newly created bucket.
   ![Access Policy](https://github.com/klurpicolo/dataframe-cleaner/assets/31367145/3136f36c-cc82-414c-98a5-357e8324b9dc)
5. Use Mongo client of your chioce, and connect to URL [mongodb://localhost:27017](mongodb://localhost:27017). Then create a new Mongo database named `dataframe_cleaner` with collection `dataframe_metadata`.
   ![Mongo Database](https://github.com/klurpicolo/dataframe-cleaner/assets/31367145/2531bb75-2848-4e3d-b235-b264a817a212)
6. Access [localhost:8000](http://localhost:8000/) to use Data Cleaner.

## Further Suggestions for Production Use
These suggestions aim to enhance the project for production, some of which were deferred due to time constraints:

### Feature
- Parameterize constants like category thresholds for user customization.
- Implement version rollback and processing from specific versions.
- Enable pagination for dataframe API to facilitate viewing large datasets.
- Implement user authentication and authorization.
- Provide detailed explanations in the UI about decision processes for user clarity.
- The current approach of fetching progress status involves constant pooling every 1 second. This is not ideal as it creates unnecessary connections to the backend. It would be better to use Long pooling, Server-Sent Events (SSE) or Websockets.

### Backend
- Implement robust transaction handling across data sources.
- Modularize the dataframe processing app for better backend isolation.
- Set up MINIO retention policies for efficient disk space management.
- Segregate servers for user requests and data processing to facilitate load scaling.
- Consider email notifications for users upon completion of data processing for better user experience with large datasets.

### Frontend
- Transition to TypeScript for improved type consistency.
- Integrate Redux for better state management.
- Add a proper styling to frontend

### Testing
- Develop Postman test scripts.
- Conduct integration tests for both backend and frontend.
- Perform load testing on dataframe processing.
