pipeline {
    agent any
    
    options {
        disableConcurrentBuilds()
    }
    
    environment {
        CI = 'true'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Clean Environment') {
            steps {
                sh 'docker-compose -p cloud-a2-ci -f docker-compose.jenkins.yml down --remove-orphans || true'
                sh 'docker system prune -f || true'
            }
        }
        
        stage('Build & Deploy') {
            steps {
                sh 'docker-compose -p cloud-a2-ci -f docker-compose.jenkins.yml up -d --build'
            }
        }
        
        stage('Verify') {
            steps {
                sh 'sleep 10'
                sh 'docker ps | grep cloud-a2-webapp-ci && echo "Container is running"'
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose -p cloud-a2-ci -f docker-compose.jenkins.yml logs --tail=100'
        }
        success {
            echo 'Build and deployment successful! The application is available at http://13.49.246.25:8095'
        }
        failure {
            echo 'Build or deployment failed!'
            sh 'docker-compose -p cloud-a2-ci -f docker-compose.jenkins.yml down || true'
        }
    }
}
