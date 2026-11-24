pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        skipDefaultCheckout()
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
    }

    environment {
        DOCKER_IMAGE = 'stenythomas/project4-app'
        CI_IMAGE = "project4-app:ci-${BUILD_NUMBER}"
        CI_DB_PASSWORD = ''
        CI_ROOT_PASSWORD = ''
        CI_SECRET_KEY = ''
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                script {
                    env.CI_DB_PASSWORD = UUID.randomUUID().toString()
                    env.CI_ROOT_PASSWORD = UUID.randomUUID().toString()
                    env.CI_SECRET_KEY = UUID.randomUUID().toString()
                }

                sh '''
                    mkdir -p security-reports
                    python3 -m venv .ci-venv
                    .ci-venv/bin/pip install --upgrade pip
                    .ci-venv/bin/pip install bandit pip-audit
                '''
            }
        }

        stage('SAST - Bandit') {
            steps {
                script {
                    def result = sh(
                        script: '''
                            .ci-venv/bin/bandit \
                            -r project4/project4 \
                            -f html \
                            -o security-reports/sast-report.html
                        ''',
                        returnStatus: true
                    )

                    if (result == 1) {
                        unstable('Bandit reported security issues')
                    } else if (result != 0) {
                        error('Bandit execution failed')
                    }
                }
            }
        }

        stage('Dependency Scan - pip-audit') {
            steps {
                sh '''
                    .ci-venv/bin/pip-audit \
                    -r project4/requirements.txt \
                    -f json \
                    -o security-reports/dependency-report.json
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                    -t "$CI_IMAGE" \
                    project4/
                '''
            }
        }

        stage('Start CI Environment') {
            steps {
                dir('project4') {
                    sh '''
                        docker compose \
                        -p project4-ci \
                        -f docker-compose.ci.yml \
                        up -d --wait

                        docker compose \
                        -p project4-ci \
                        -f docker-compose.ci.yml ps
                    '''
                }
            }
        }

        stage('Database Migrations') {
            steps {
                dir('project4') {
                    sh '''
                        docker compose \
                        -p project4-ci \
                        -f docker-compose.ci.yml \
                        exec -T web \
                        python manage.py migrate --noinput

                        docker compose \
                        -p project4-ci \
                        -f docker-compose.ci.yml \
                        exec -T web \
                        python manage.py migrate --check
                    '''
                }
            }
        }

        stage('Application Testing') {
            steps {
                dir('project4') {
                    sh '''
                        docker compose \
                        -p project4-ci \
                        -f docker-compose.ci.yml \
                        exec -T web \
                        python manage.py check --database default

                        docker compose \
                        -p project4-ci \
                        -f docker-compose.ci.yml \
                        exec -T web \
                        python manage.py makemigrations \
                        --check --dry-run

                        curl --fail --silent --show-error \
                        --retry 10 \
                        --retry-connrefused \
                        --retry-delay 3 \
                        http://127.0.0.1:8001/ \
                        -o /dev/null

                        echo "Application smoke test passed"
                    '''
                }
            }
        }

        stage('DAST - OWASP ZAP') {
            steps {
                script {
                    def zapStatus = sh(
                        script: '''
                            mkdir -p zap-output
                            chmod 777 zap-output

                            docker run --rm \
                            --network host \
                            -v "$WORKSPACE/zap-output:/zap/wrk/:rw" \
                            ghcr.io/zaproxy/zaproxy:stable \
                            zap-baseline.py \
                            -t http://127.0.0.1:8001 \
                            -m 1 \
                            -r dast-report.html

                            result=$?
                            exit "$result"
                        ''',
                        returnStatus: true
                    )

                    sh '''
                        if [ -f zap-output/dast-report.html ]; then
                            cp zap-output/dast-report.html \
                            security-reports/
                        fi
                    '''

                    if (zapStatus == 2) {
                        unstable('ZAP reported security warnings')
                    } else if (zapStatus != 0) {
                        error("ZAP failed with exit code ${zapStatus}")
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            when {
                expression {
                    currentBuild.currentResult == 'SUCCESS'
                }
            }

            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        export DOCKER_CONFIG="$(mktemp -d)"
                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT

                        printf '%s' "$DOCKER_TOKEN" | \
                        docker login \
                        -u "$DOCKER_USER" \
                        --password-stdin

                        docker tag "$CI_IMAGE" \
                        "$DOCKER_IMAGE:$BUILD_NUMBER"

                        docker tag "$CI_IMAGE" \
                        "$DOCKER_IMAGE:latest"

                        docker push "$DOCKER_IMAGE:$BUILD_NUMBER"
                        docker push "$DOCKER_IMAGE:latest"

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'security-reports/*',
                allowEmptyArchive: true
            )

            dir('project4') {
                sh '''
                    docker compose \
                    -p project4-ci \
                    -f docker-compose.ci.yml \
                    down -v --remove-orphans || true
                '''
            }
        }

        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        unstable {
            echo 'Security findings require review. Image publishing skipped.'
        }

        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}
