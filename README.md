## Limitation
- The current implemenation requires Chula Genie as the main LLM service. The substitution of other LLMs might require some extra efforts.

## To develop

0. Create Google AI account and get API KEY and setup AWS S3 bucket with credentials
1. go to `/llm-service` folder and copy `.env.template` file to `.env` and set the environment variables
1. run `docker compose up -d` to start all services. Note that the Voice Generator may take very long to download the model.
2. run `n8n:import:workflows` to import all workflows in the `/workflows` folder
3. open n8n at http://localhost:5678 and publish the following workflows: outline-generator, Course API Workflow, async-generate-slide-v2, async-generate-exercise, Analytics, Notification API workflow, RAG, and CRUD Lesson
4. enter the required credentials on the above workflows


## Development URLs

| Service           | URL                          |
| ----------------- | ---------------------------- |
| n8n               | http://localhost:5678        |
| Slide Generator   | http://localhost:5001        |
| LLM Service       | http://localhost:8080        |
| Voice Generator   | http://localhost:8000        |
