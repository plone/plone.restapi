#!groovy

pipeline {

  agent {
    label 'jmeter'
  }

  triggers{
    cron('H 23 * * *')
  }

  options {
    buildDiscarder(logRotator(numToKeepStr:'100'))
    // timeout(time: 60, unit: 'MINUTES')
    disableConcurrentBuilds()
  }

  stages {

    // Performance Tests
    stage('Performance Tests') {

      steps {
        deleteDir()
        checkout scm
        sh "python3 -m venv ."
        sh "bin/pip install -r requirements-6.0.txt"
        sh "bin/buildout -c plone-6.0.x-performance.cfg"
        sh "bin/instance start"
        sh "sleep 20"

        sh "jmeter -n -t performance.jmx -l performance-jmeter-unfiltered.csv"
        sh '/opt/jmeter/bin/FilterResults.sh --input-file performance-jmeter-unfiltered.csv --output-file performance-jmeter.csv --exclude-label-regex true --exclude-labels ".*Testfolder.*"'
        sh "rm performance-jmeter-unfiltered.csv"

        sh "jmeter -n -t querystring-search.jmx -l performance-querystring-search-unfiltered.csv"
        sh '/opt/jmeter/bin/FilterResults.sh --input-file performance-querystring-search-unfiltered.csv --output-file performance-querystring-search.csv --exclude-label-regex true --exclude-labels ".*Testfolder.*"'
        sh "rm performance-querystring-search-unfiltered.csv"

        sh "jmeter -n -t volto.jmx -l performance-volto-unfiltered.csv"
        sh '/opt/jmeter/bin/FilterResults.sh --input-file performance-volto-unfiltered.csv --output-file performance-volto.csv --exclude-label-regex true --exclude-labels ".*Testfolder.*"'
        sh "rm performance-volto-unfiltered.csv"

        sh "bin/pip install locust"
        sh "make test-performance-locust-querystring-search-ci"
        sh "ls -al performance"
        // sh "bin/python performance/convert.py -p example_stats.csv"
        // sh "bin/locust -f performance/images.py --no-web -c 100 -r 10 --run-time 1m --host http://localhost:12345/Plone"

        sh "bin/instance stop"

      }
      post {
        always {
          perfReport '**/performance-*.csv'
          archiveArtifacts artifacts: '**/performance-*.csv', fingerprint: true, allowEmptyArchive: true
        }
      }
    }
  }
}

