#!/bin/bash

echo "=== Обновление репозитория Apache Airflow ==="
helm repo update

echo "=== Запуск Minikube ==="
minikube start

echo "=== Ожидание 7 минут для полного запуска всех подов ==="
echo "Ожидание началось: $(date)"
sleep 420  # 7 минут = 420 секунд
echo "Ожидание завершено: $(date)"

echo "=== Запуск скрипта install_kafka_packages.sh ==="
# Загружаем и запускаем скрипт установки Kafka пакетов
curl -s https://raw.githubusercontent.com/Kh-1976/scripts/main/install_kafka_packages.sh | bash

echo "=== Все операции завершены ==="
