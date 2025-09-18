import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor


class AsyncSQLite:
    def __init__(self, db_path):
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def _execute(self, query, params=None):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._sync_execute,
            query,
            params
        )

    def _sync_execute(self, query, params):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")  # Modo WAL
            conn.execute("PRAGMA synchronous=NORMAL")  # Optimización para WAL
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            conn.commit()
            return cursor.rowcount

    # Operaciones CRUD asíncronas
    async def insert_data(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return await self._execute(query, tuple(data.values()))

    async def query_data(self, table: str, conditions=None):
        query = f"SELECT * FROM {table}"
        params = []
        if conditions:
            query += " WHERE " + " AND ".join([f"{k}=?" for k in conditions])
            params = list(conditions.values())
        return await self._execute(query, params)

    async def update_data(self, table: str, updates, where):
        set_clause = ', '.join([f"{k}=?" for k in updates])
        where_clause = ' AND '.join([f"{k}=?" for k in where])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = list(updates.values()) + list(where.values())
        return await self._execute(query, params)

    async def get_columns(self, table: str) -> list:
        """
        Obtiene los nombres de las columnas de una tabla
        Args:
            table: Nombre de la tabla
        Returns:
            Lista de nombres de columnas ordenadas
        """
        query = "PRAGMA table_info(?)"
        result = await self._execute(query, (table,))
        return [column[1] for column in sorted(result, key=lambda x: x[0])]

    async def delete_data(self, table: str, conditions: dict) -> int:
        """
        Elimina registros que cumplan con las condiciones especificadas
        Args:
            table: Nombre de la tabla
            conditions: Diccionario con condiciones {columna: valor}
        Returns:
            Número de registros eliminados
        """
        if not conditions:
            raise ValueError(
                "Se requieren condiciones para eliminación segura")

        where_clause = " AND ".join([f"{k}=?" for k in conditions])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        params = list(conditions.values())

        return await self._execute(query, params)
