pipeline {
    agent any

    environment {
        // Create immutable image tags using BUILD_NUMBER + Git SHA
        IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT}"
        PYTHONPATH = "backend"
        // Use credentials for real DB instead of hardcoded sqlite, for production
        // But for this CI test environment we connect to our local docker-compose postgres
        SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:postgres@host.docker.internal:5433/adaptive_mlops_test"
        ADMIN_API_KEY = "secret-admin-key"
        SECRET_KEY = "ci-secret-key-for-testing"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'printf "SECRET_KEY=ci-secret-key-for-testing\nADMIN_API_KEY=secret-admin-key\n" > backend/.env'
            }
        }
        
        stage('Environment & DB Setup') {
            steps {
                echo "Setting up environment variables..."
                sh 'python -m pip install -e backend/[test]'
                dir('frontend') {
                    sh 'npm install'
                }
                echo "Spinning up Test DB..."
                sh 'docker-compose -f docker-compose.test.yml up -d db-test'
                // Wait for postgres to be ready
                sh 'sleep 5'
                dir('backend') {
                    sh 'python -m alembic upgrade head'
                }
            }
        }

        stage('Lint') {
            steps {
                sh 'python scripts/ci/lint.py'
                dir('frontend') {
                    sh 'npm run lint'
                }
            }
        }

        stage('Unit Tests') {
            steps {
                // Backend tests
                sh 'python scripts/ci/unit_tests.py'
                // Frontend type checking (simulating tests)
                dir('frontend') {
                    sh 'npm run build'
                }
            }
            post {
                always {
                    junit 'backend/junit-report.xml'
                }
            }
        }

        stage('Data Validation') {
            steps {
                sh 'python scripts/ci/data_validation.py'
            }
        }

        stage('Train Candidate') {
            steps {
                // Real execution using app logic
                sh 'python scripts/ci/train_candidate.py'
            }
        }

        stage('Evaluate') {
            steps {
                sh 'python scripts/ci/evaluate.py'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'metrics/*.json', allowEmptyArchive: true
                }
            }
        }

        stage('Quality Gate') {
            steps {
                sh 'python scripts/ci/quality_gate.py'
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker images with tag ${env.IMAGE_TAG}"
                sh 'docker build -t adaptive-mlops-backend:${IMAGE_TAG} ./backend'
                sh 'docker build -t adaptive-mlops-frontend:${IMAGE_TAG} ./frontend'
            }
        }

        stage('Integration & Selenium Tests') {
            steps {
                // Starts server in background, runs tests, then kills it
                sh 'python scripts/ci/integration_tests.py'
                sh 'python scripts/ci/selenium_tests.py'
            }
        }
    }

    post {
        always {
            sh 'docker-compose -f docker-compose.test.yml down -v || true'
            archiveArtifacts artifacts: 'logs/*.log, test-reports/*.xml', allowEmptyArchive: true
            echo "Archiving complete"
        }
        failure {
            echo "Pipeline failed. Check logs and artifact archives."
        }
    }
}
