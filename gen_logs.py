import json
from faker import Faker
from datetime import datetime, timedelta
import uuid
import random
import time
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

faker = Faker()

# Kafka config - FIXED for cross-namespace access
KAFKA_BOOTSTRAP_SERVERS = ["my-kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"]
KAFKA_TOPIC = ['logs-debug', 'logs-info', 'logs-error', 'logs-warning', 'logs-critical', 'logs-trace']

# Создание топика если не существует
admin_conf = {'bootstrap.servers': ','.join(KAFKA_BOOTSTRAP_SERVERS)}
admin_client = AdminClient(admin_conf)

print(f"Checking if topics exist...")
existing_topics = admin_client.list_topics().topics

for i in KAFKA_TOPIC: 
    if i not in existing_topics:
        print(f"Topic '{i}' not found. Creating...")
        new_topic = NewTopic(i, num_partitions=3, replication_factor=1)
        fs = admin_client.create_topics([new_topic])

        for topic, future in fs.items():
            try:
                future.result()
                print(f"✅ Topic '{topic}' created successfully")
            except Exception as e:
                print(f"❌ Failed to create topic '{topic}': {e}")
                exit(1)
    else:
        print(f"✅ Topic '{i}' already exists")

# Инициализация Producer
conf = {
    'bootstrap.servers': ','.join(KAFKA_BOOTSTRAP_SERVERS),
    'acks': 'all',
    'retries': 3,
    'enable.idempotence': True,
    'message.timeout.ms': 10000,
}
producer = Producer(conf)


def delivery_report(err, msg):
    """Callback для подтверждения доставки"""
    if err is not None:
        print(f'❌ Message delivery failed: {err}')
    else:
        print(f'✅ Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


# Возможные уровни логирования
levels = ['DEBUG', 'DEBUG', 'INFO', 'WARNING', 'DEBUG', 'ERROR', 'INFO', 'CRITICAL',
          'DEBUG', 'DEBUG', 'DEBUG', 'DEBUG', 'DEBUG', 'TRACE', 'INFO', 'DEBUG']

# Возможные сервисы
services = ['auth-service', 'database', 'payment-processor', 'disk-monitor', 'scheduler',
            'web-server', 'cache', 'email-service', 'api-gateway', 'rate-limiter',
            'user-service', 'app', 'health-check']

methods = ['UserService.findUserByEmail', 'UserService.createUser', 'UserService.updateUserProfile',
           'UserService.deleteUser', 'UserService.changePassword', 'UserService.verifyEmail', 'UserService.blockUser',
           'EmailService.sendWelcomeEmail', 'EmailService.sendPasswordReset', 'EmailService.sendBulkEmails',
           'NotificationService.sendTelegramMessage', 'NotificationService.deleteNotification',
           'TemplateService.loadTemplate', 'TemplateService.saveTemplate', 'TemplateService.deleteTemplate',
           'QueueService.pushToQueue', 'QueueService.getQueueLength', 'QueueService.pauseQueue']

functions = ['UserService', 'EmailService', 'NotificationService', 'TemplateService', 'QueueService']

# Шаблоны сообщений для разных уровней
messages = {
    'DEBUG': [
        'Попытка аутентификации пользователя \'{user}\' с IP {ip}',
        'Ключ \'{key}\' не найден в Redis, выполняем запрос к БД',
        'Вызов метода {method} с параметром id = {msgid}',
        'Вызов метода {method} с параметром id = {id}',
        'Загружена конфигурация приложения из файла {config_file}',
        'SQL запрос: SELECT * FROM {dbs} WHERE email = \'{email}\';',
        'SQL запрос: SELECT {columns} FROM {dbs} WHERE user = \'{user}\';',
        'SQL запрос: SELECT {columns} FROM {dbs} WHERE ip = \'{ip}\';',
        'SQL запрос: SELECT {columns} FROM {dbs} WHERE role = \'{role}\';',
        'Кэш-промах для ключа {msgid}, время загрузки из БД: {time} мс',
        'Парсинг JSON ответа от API {url} завершен, размер данных: {space}0 Mb',
        'Делегирование вызова в {method}()',
        'Обработка callback от платежного шлюза',
        'Запуск шедулера: ежедневная задача очистки',
        'Очистка кэша по паттерну {user}:* (удалено 150 ключей)',
        'Сохранение в кэш: user: {user}, TTL: 3600с',
        'Проверка уникальности: email: {email} - {result}',
        'Ошибка валидации: поле email: {user}{err_email} не соответствует формату',
        'Чтение файла: {path}',
        'Загрузка модуля: {method}'
    ],
    'INFO': [
        'Пользователь \'{user}\' успешно вошёл в систему (роль: {role})',
        'Запущена ежедневная задача архивации логов',
        'Отправлено письмо сброса пароля на {email} (message-id: <{msgid}>)',
        'Все сервисы работают в штатном режиме (status: UP)',
        'Приложение успешно запущено за {time} мс',
        'Миграция базы данных выполнена успешно (версия: {space}00)',
        'Получен новый заказ #{msgid} на сумму {amount} руб.',
        'Резервное копирование завершено, сохранено {count} файлов',
        'Обновление данных выполнено, затронуто {count} записей'
    ],
    'WARNING': [
        'Медленный запрос ({time} с): {query}',
        'Высокая загрузка CPU: {cpu}% в течение последних 5 минут',
        'Превышен лимит запросов для клиента {ip}, запрос отклонён',
        'Закончились свободные соединения в пуле, создано {count} новых',
        'Использование оперативной памяти достигло {cpu}%',
        'SSL сертификат истекает через {days} дней',
        'Повторная попытка подключения к {method} через {days} секунд',
        'Обнаружены подозрительные запросы с IP {ip}, запросы ограничены'
    ],
    'ERROR': [
        'Не удалось обработать платёж #{order}: недостаточно средств на счёте',
        'Ошибка валидации JWT токена: SignatureException – подпись недействительна',
        'Исключение: SQLIntegrityConstraintViolationException: a:145',
        'Исключение: PaymentController.handle(PaymentController.java:78)',
        'Ошибка подключения к базе данных: Connection refused',
        'Не удалось отправить email на адрес {email}: SMTP error',
        'Ошибка парсинга: ожидался файл {config_file}, получен null',
        'Файл не найден по пути {path}',
        'Таймаут при выполнении запроса к {path} после {days} мс',
        'Не удалось сохранить файл: недостаточно прав на запись'
    ],
    'CRITICAL': [
        'Свободное место на диске /dev/sda{days} упало ниже 5% (осталось {space} ГБ)',
        'Непойманное исключение в потоке main: {exceptions}',
        'Приложение аварийно завершилось с кодом: {exit_code}',
        'Потеряно соединение с кластером баз данных, переключение не удалось',
        'Обнаружена критическая уязвимость в модуле {method}, требуется немедленное обновление',
        'Отказ всех реплик сервиса {function}, сервис недоступен',
        'Достигнут критический порог использования памяти: {cpu}%'
    ],
    'TRACE': [
        'Вызов метода {method}() с параметром {param} = {value}',
        'Вход в функцию {function} с аргументами {args}',
        'Выход из функции {function}, возвращаемое значение: {result}',
        'Получен сырой запрос: {raw_data}',
        'Отправлен ответ: {response_data}',
        'Начало транзакции {id}',
        'Коммит транзакции {id} завершен'
    ]
}

print("🚀 Starting log generation...")
print(f"📨 Sending logs to Kafka topics: {KAFKA_TOPIC}")
print(f"🔗 Kafka bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
print("-" * 50)

# Бесконечный цикл генерации логов
while True:
    try:
        level = random.choice(levels)
        service = random.choice(services)
        msg_template = random.choice(messages[level])

        random_user = faker.user_name()
        random_ip = faker.ipv4()
        random_email = faker.email()
        random_uuid = str(uuid.uuid4())
        random_id = random_uuid[:8]

        try:
            message = msg_template.format(
                user=random_user,
                ip=random_ip,
                role=random.choice(['user', 'admin', 'guest', 'moderator', 'superadmin']),
                key=f'user_profile:{random_id}',
                id=random_uuid,
                time=round(random.uniform(0.5, 15.0), 2),
                cpu=random.randint(65, 99),
                order=f'ORD-{random_id[:10]}',
                space=round(random.uniform(0.5, 15.0), 1),
                email=random_email,
                msgid=random_id,
                query=f"SELECT * FROM {random.choice(['orders', 'users', 'products'])} WHERE id = '{random_id}'",
                method=random.choice(methods),
                param=random.choice(['id', 'email', 'userId', 'orderId', 'productId']),
                value=random_id,
                function=random.choice(functions),
                args={'id': random_id, 'email': random_email},
                result=random.choice(['success', 'failure', 'timeout', 'cancelled']),
                raw_data=json.dumps({'event': 'user_login', 'user': random_user}),
                response_data=json.dumps({'status': random.choice(['ok', 'error'])}),
                config_file=f"{faker.word()}{random.choice(['.yaml', '.json', '.conf', '.properties'])}",
                url=faker.url(),
                amount=random.randint(100, 999999),
                count=random.randint(1, 5000),
                days=random.randint(1, 30),
                path=f"/var/log/{faker.word()}/{faker.word()}.log",
                exit_code=random.choice(['1', '137', '139', '143', '255']),
                exceptions=random.choice(['NullPointerException', 'OutOfMemoryError', 'StackOverflowError',
                                          'IllegalStateException', 'IOException', 'TimeoutException']),
                columns=random.choice(['id, name, email', 'id, product, price', 'user_id, action, timestamp',
                                       'order_id, status, total', 'id, created_at, updated_at']),
                err_email=random.choice(['missing@', 'invalid@', 'none@', 'bad@format']),
                dbs=random.choice(['users', 'orders', 'products', 'payments', 'sessions', 'logs'])
            )
        except KeyError as e:
            print(f"⚠️ KeyError in message formatting: {e}")
            message = f"Log message template error: {msg_template}"

        current_time = datetime.now()
        timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'service': service,
            'message': message,
            'host': faker.hostname(),
            'pid': random.randint(1000, 9999)
        }

        key_bytes = service.encode('utf-8')
        value_bytes = json.dumps(log_entry, ensure_ascii=False).encode('utf-8')
        
        # Отправка в соответствующий топик
        topic_map = {
            'DEBUG': KAFKA_TOPIC[0],
            'INFO': KAFKA_TOPIC[1],
            'ERROR': KAFKA_TOPIC[2],
            'WARNING': KAFKA_TOPIC[3],
            'CRITICAL': KAFKA_TOPIC[4],
            'TRACE': KAFKA_TOPIC[5]
        }
        
        producer.produce(
            topic_map[level],
            key=key_bytes,
            value=value_bytes,
            callback=delivery_report
        )
        producer.poll(0)
        remaining = producer.flush(timeout=5)
        if remaining > 0:
            print(f"⚠️ {remaining} messages still pending")

        print(f"📤 Sent: {level} from {service} - {message[:50]}...")
        print("-" * 50)

        time.sleep(random.uniform(1, 5))

    except KeyboardInterrupt:
        print("\n🛑 Stopping log generation...")
        producer.flush()
        break
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        time.sleep(10)

print("👋 Log generator stopped")
