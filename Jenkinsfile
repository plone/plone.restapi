#!groovy

pipeline {

  agent any

  triggers{
    cron('H 23 * * *')
  }

  options {
    buildDiscarder(logRotator(numToKeepStr:'100'))
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
  }

  stages {

    // Performance Tests
    stage('Performance Tests') {
      agent {
        label 'node'
      }
      steps {
        deleteDir()
        checkout scm
        sh "virtualenv ."
        sh "bin/pip install -r requirements.txt"
        sh "bin/buildout -c plone-5.2.x-performance.cfg"
        sh "bin/instance start"
        sh "sleep 20"

        // sh "jmeter -n -t performance.jmx -l jmeter.csv"
        sh "bin/pip install locust"
        sh "bin/locust -f performance/images.py --no-web -c 100 -r 10 --run-time 1m --host http://localhost:12345/Plone"

        sh "bin/instance stop"
      }
      post {
        always {
          perfReport '**/jmeter.csv'
        }
      }
    }
  }
}

