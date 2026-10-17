import os
import traceback
import logging
from django.db import connection
from django.db.utils import DatabaseError

# Настройка логгера для ошибок БД
os.makedirs('logs', exist_ok=True)
logger = logging.getLogger('db_errors')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler('logs/db_errors.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def call_procedure(name, params=(), out_count=0, fetch=True):
    """
    Универсальный вызов хранимой процедуры с поддержкой OUT-параметров.
    """
    in_placeholders = ','.join(['%s'] * len(params))
    out_vars = [f"@out{i}" for i in range(out_count)]
    
    all_args = [in_placeholders] + out_vars if params else out_vars
    placeholders = ','.join(filter(None, all_args))

    sql = f"CALL {name}({placeholders})"

    try:
        with connection.cursor() as cur:
            # 1. Выполняем саму процедуру
            cur.execute(sql, list(params))
            
            # Важно: mysqlclient иногда требует "вычитывания" всех результатов
            # если процедура что-то возвращает. Для INSERT/UPDATE это не критично.
            if fetch:
                rows = cur.fetchall()
            else:
                rows = None

            # 2. Получаем значения OUT-переменных отдельным запросом
            out_values = []
            if out_count > 0:
                # Если предыдущий запрос вернул результаты, их нужно очистить
                while cur.nextset():
                    pass
                
                select_sql = f"SELECT {', '.join(out_vars)}"
                cur.execute(select_sql)
                out_values = list(cur.fetchone())
                
        return rows, out_values
        
    except DatabaseError as e:
        logger.error(f"Ошибка при вызове процедуры {name} с параметрами {params}:\n{traceback.format_exc()}")
        raise e

def call_function(name, params=()):
    """Вызов хранимой функции, возвращающей скаляр."""
    placeholders = ','.join(['%s'] * len(params))
    sql = f"SELECT {name}({placeholders})"
    try:
        with connection.cursor() as cur:
            cur.execute(sql, list(params))
            return cur.fetchone()[0]
    except DatabaseError as e:
        logger.error(f"Ошибка при вызове функции {name} с параметрами {params}:\n{traceback.format_exc()}")
        raise e