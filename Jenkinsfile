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
        sh "jmeter -n -t performance.jmx -l jmeter.jtl"
        sh "bin/instance stop"
      }
      post {
        always {
         performanceReport parsers: [[$class: 'JMeterParser', glob: "jmeter.jtl"]], sourceDataFiles: "jmeter.jtl", errorFailedThreshold: 1, errorUnstableThreshold: 1, ignoreFailedBuild: false, ignoreUnstableBuild: false, relativeFailedThresholdNegative: 0, relativeFailedThresholdPositive: 0, relativeUnstableThresholdNegative: 0, relativeUnstableThresholdPositive: 0
        }
      }
    }
  }
}

