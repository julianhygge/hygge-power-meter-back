import datetime
from peewee import DateTimeField, OperationalError
from playhouse.pool import PooledPostgresqlDatabase
from playhouse.signals import Model
from hyggepowermeter.config.configuration import CONFIGURATION


class Database:
    def __init__(self, conf):
        """Initializes the Database instance with configuration."""
        self._db_instance = None
        self._configuration = conf

    def get_instance(self):
        """Gets the database instance, creating a new one if necessary."""
        if self._db_instance is None or not self._test_connection():
            self._db_instance = self._create_db_instance()
        return self._db_instance

    def _test_connection(self):
        """Tests the current database connection."""
        try:
            self._db_instance.execute_sql('SELECT 1;')
            return True
        except OperationalError:
            self._db_instance.close()
            return False

    def _create_db_instance(self):
        """Creates a new database instance with pooled connections."""
        db_instance = PooledPostgresqlDatabase(
            self._configuration.database,
            user=self._configuration.user,
            password=self._configuration.password,
            host=self._configuration.host,
            port=self._configuration.port,
            max_connections=self._configuration.max_connections,
            stale_timeout=self._configuration.stale_timeout,
            autorollback=True
        )
        self._set_utc_timezone(db_instance)
        return db_instance

    @staticmethod
    def _set_utc_timezone(db_ins):
        """Sets the timezone of the database connection to UTC."""
        with db_ins.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SET TIME ZONE 'UTC';")


class BaseModel(Model):
    """Base model for Peewee ORM that sets the database dynamically."""

    @classmethod
    def set_database(cls, db):
        """Sets the database for the model."""
        cls._meta.database = db.get_instance()  # type: ignore


class InfDateTimeField(DateTimeField):
    """DateTime field that supports 'infinity' and '-infinity' values."""

    def db_value(self, value):
        """Converts Python datetime values to database string representation."""
        if value == datetime.datetime.max:
            return 'infinity'
        elif value == datetime.datetime.min:
            return '-infinity'
        else:
            return super().db_value(value)


database = Database(CONFIGURATION.db)
