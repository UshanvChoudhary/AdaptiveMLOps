# Jenkins Local Setup Guide

## Requirements
- Docker and Docker Compose
- Java 11+
- Jenkins (either standalone or via Docker)

## Running Jenkins via Docker
To quickly spin up a local Jenkins instance with Docker support:
```bash
docker run -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

## Configuration Steps
1. Navigate to `http://localhost:8080` in your browser.
2. Retrieve the initial admin password from the docker logs.
3. Install the **suggested plugins**.
4. Install additional required plugins:
   - **Docker Pipeline**
   - **JUnit Plugin**
5. Create an admin user.

## Setting Up the Pipeline
1. On the Jenkins dashboard, click **New Item**.
2. Enter `adaptive-mlops-ci` and select **Pipeline**, then click OK.
3. Scroll down to the **Pipeline** section.
4. Set **Definition** to **Pipeline script from SCM**.
5. Set **SCM** to **Git** and provide your repository URL.
6. Set the **Script Path** to `Jenkinsfile`.
7. Click **Save**.

## Running the Pipeline
- Click **Build Now** to trigger the CI pipeline.
- The pipeline will run through Checkout, Environment setup, Linting, Unit Testing, Data Validation, Model Training, Evaluation, Quality Gates, Docker Builds, and Integration/Selenium tests.
- Build artifacts like test reports, ML evaluation logs, and model metrics will be archived upon completion.
