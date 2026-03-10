#!/bin/bash

# Получаем имя пода scheduler
SCHEDULER_NAME=$(minikube kubectl -- get pods -n airflow -l component=scheduler -o jsonpath="{.items[0].metadata.name}")
# Получаем имя пода worker
WORKER_POD=$(minikube kubectl -- get pods -n airflow -l component=worker -o jsonpath="{.items[0].metadata.name}")
# Получаем имя пода dag-processor
DAG_POD=$(minikube kubectl -- get pods -n airflow -l component=dag-processor -o jsonpath="{.items[0].metadata.name}")
# Получаем имя пода triggerer
TRIGGER_POD=$(minikube kubectl -- get pods -n airflow -l component=triggerer -o jsonpath="{.items[0].metadata.name}")

# Функция для установки пакетов в под
install_packages() {
    local pod_name=$1
    local pod_type=$2
    
    echo "Installing packages in $pod_type pod: $pod_name"
    # -it не указывать. В интерактивном режиме после добавления библиотек в scheduler скрипт будет прирываться.
    # То есть в интерактивном режиме после первого удачного выполнения происходит остановка.
    minikube kubectl -- exec $pod_name -n airflow -- /bin/bash -c "
        echo 'Upgrading pip...' &&
        pip install --upgrade pip &&
        echo 'Installing required packages...' &&
        pip install confluent-kafka kafka-python faker &&
        echo 'Package installation completed in $pod_type pod'
    "
}

# Устанавливаем пакеты во все поды
install_packages "$SCHEDULER_NAME" "scheduler"
install_packages "$WORKER_POD" "worker"
install_packages "$DAG_POD" "dag-processor"
install_packages "$TRIGGER_POD" "triggerer"

echo "All packages installed successfully in all pods!"
