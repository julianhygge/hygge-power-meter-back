from hyggepowermeter.data.energy_system_schemas import db
from hyggepowermeter.utils.logger import logger


class RepositoryBase:
    def __init__(self, db_config):
        db.init(database=db_config.database,
                host=db_config.host,
                port=db_config.port,
                user=db_config.user,
                password=db_config.password)

    @staticmethod
    def _insert(table_class, data):
        try:
            with db.atomic():
                record = table_class.create(**data)
                logger.info(f"Inserted record with ID {record.id} into {table_class.get_table_name()}.")
                return record
        except Exception as e:
            logger.error(f"Error inserting record into {table_class.get_table_name()}: {e}")
            return None

    @staticmethod
    def _read(table_class, filters=None, order_by=None, limit=None, between=None, as_iterator=False):
        try:
            query = table_class.select()
            if filters:
                query = query.where(*filters)

            if between:
                start_time, end_time = between
                query = query.where((table_class.timestamp >= start_time) & (table_class.timestamp < end_time))

            if order_by:
                query = query.order_by(*order_by)

            if limit:
                query = query.limit(limit)

            if as_iterator:
                return query.iterator()

            records = list(query)
            logger.info(f"Read {len(records)} records from {table_class.get_table_name()}.")
            return records
        except Exception as e:
            logger.error(f"Error reading records from {table_class.get_table_name()}: {e}")
            return []

    @staticmethod
    def _create_table_if_not_exists(table_class):
        if not table_class.table_exists():
            table_class.create_table()
            logger.info(f"Table {table_class.get_table_name()} created.")
        else:
            logger.info(f"Table {table_class.get_table_name()} already exists.")

    @staticmethod
    def _create_schema_if_not_exists(schema_name):
        try:
            # Check if the schema exists
            db.execute_sql(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
            logger.info(f"Schema {schema_name} created or already exists.")
        except db as e:
            logger.error(f"Error creating schema {schema_name}: {e}")
