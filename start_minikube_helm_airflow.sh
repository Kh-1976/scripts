#!/bin/bash

echo "=== Запуск Minikube ==="
minikube start

echo "=== Обновление репозитория Apache Airflow ==="
helm repo update

echo "=== Ожидание 7 минут для полного запуска всех подов ==="
echo "Ожидание началось: $(date)"
sleep 420  # 7 минут = 420 секунд
echo "Ожидание завершено: $(date)"

echo "=== Запуск скрипта install_kafka_packages.sh ==="
# Загружаем и запускаем скрипт установки Kafka пакетов
curl -s https://raw.githubusercontent.com/Kh-1976/minikube_data/main/install_kafka_packages.sh | bash

echo "=== Все операции завершены ==="
