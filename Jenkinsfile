#!groovy

pipeline {

  agent any

  options {
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
  }

  stages {

    // Performance Tests
    stage('Performance Tests') {
      agent {
        label 'master'
      }
      steps {
        deleteDir()
        checkout scm
        sh "virtualenv ."
        sh "bin/pip install -r requirements.txt"
        sh "bin/buildout -c plone-5.1.x-performance.cfg"
        sh "bin/instance start"
        sh "sleep 10"
        sh "jmeter -n -t performance.jmx"
        sh "bin/instance stop"
      }
    }
  }
}

