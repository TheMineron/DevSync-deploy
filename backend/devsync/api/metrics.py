from prometheus_client import Gauge


online_users = Gauge(
    'online_users_count',
    'Количество активных пользователей на сайте',
    ['app']
)

online_users.labels(app='devsync').set(0)