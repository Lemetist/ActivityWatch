#!/bin/bash

# Скрипт для автоматического обновления SSL сертификатов Let's Encrypt
# Добавьте в crontab: 0 3 * * * /root/renew-ssl.sh

cd /root

# Попытка обновить сертификаты
docker-compose run --rm certbot renew --quiet

# Проверка, были ли обновлены сертификаты
if [ $? -eq 0 ]; then
    echo "$(date): Сертификаты проверены и обновлены при необходимости"
    # Перезагрузка nginx для применения новых сертификатов
    docker-compose exec nginx nginx -s reload
    echo "$(date): Nginx перезагружен"
else
    echo "$(date): Ошибка при обновлении сертификатов"
fi
