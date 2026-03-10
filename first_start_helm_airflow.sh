#!/bin/bash

echo "=== Запуск Minikube ==="
minikube start \
  --driver=docker \
  --cpus=4 \
  --memory=8192

echo "=== Добавление и обновление репозитория Apache Airflow ==="
helm repo add apache-airflow https://airflow.apache.org
helm repo update

echo "=== Установка Airflow через Helm ==="
helm upgrade --install airflow apache-airflow/airflow \
  --namespace airflow --create-namespace \
  -f https://raw.githubusercontent.com/Kh-1976/minikube_data/main/values_git_sync.yaml

echo "=== Ожидание 7 минут для полного запуска всех подов ==="
echo "Ожидание началось: $(date)"
sleep 420  # 7 минут = 420 секунд
echo "Ожидание завершено: $(date)"

echo "=== Создание namespace kafka. Установка Strimzi. Установка Apache Kafka ==="
minikube kubectl create namespace kafka
helm install strimzi-cluster-operator oci://quay.io/strimzi-helm/strimzi-kafka-operator \
  --version 0.46.0 --namespace kafka
minikube kubectl -- apply \
  -f https://raw.githubusercontent.com/Kh-1976/minikube_data/main/kafka-kraft.yaml \
  --namespace kafka

echo "=== Установка log-generator ==="
minikube kubectl apply -- \
  -f https://raw.githubusercontent.com/Kh-1976/minikube_data/main/log-generator.yaml

echo "=== Запуск скрипта install_kafka_packages.sh ==="
# Загружаем и запускаем скрипт установки Kafka пакетов
curl -s https://raw.githubusercontent.com/Kh-1976/minikube_data/main/install_kafka_packages.sh | bash

echo "=== Все операции завершены ==="
