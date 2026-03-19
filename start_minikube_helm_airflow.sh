#!/bin/bash

echo "=== Обновление репозитория Apache Airflow ==="
helm repo update

echo "=== Запуск Minikube ==="
minikube start

echo "=== Запуск скрипта install_kafka_packages.sh ==="
# Загружаем и запускаем скрипт установки Kafka пакетов
curl -s https://raw.githubusercontent.com/Kh-1976/scripts/main/install_kafka_packages.sh | bash

echo "=== Все операции завершены ==="
