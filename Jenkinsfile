#!groovy

pipeline {

  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr:'30'))
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
    triggers{ cron(@midnight) }
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
        sh "jmeter -n -t performance.jmx -l jmeter.csv"
        // sh "cat jmeter.csv"
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

