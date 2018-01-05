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
        sh "make build"
      }
    }
  }
}

