Консольная утилита tcping (автор Рыженков Илья)
Запуск: main.py [dest_ip] [dest_port]
Аргументы:
    -h - вывод справочной информации
    -p - кол-во пакетов для отправки
    -t - timeout ожидания ответа
    -i - временой интервал отправки пакетов
    -u - режим бесконечной отправки пакетов (Можно посмотреть статистику, отправив SIGUSR1)
    -a [address] [port] - добавить дополнительный адресс для пинга
    -P [port] - исходный порт
    -v - более подробный вывод информации о каждом пакете