from peewee import OperationalError
from playhouse.pool import PooledPostgresqlDatabase


class Database:
    def __init__(self, conf, models):
        """Initializes the Database instance with configuration."""
        self._db_instance = None
        self._configuration = conf
        # Assume models is a list of your model classes.
        self.models = models

    def get_instance(self):
        """Gets the database instance, creating a new one if necessary."""
        if self._db_instance is None or not self._test_connection():
            self._db_instance = self._create_db_instance()
            self._update_model_databases()
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
        db_inst = PooledPostgresqlDatabase(
            self._configuration.database,
            user=self._configuration.user,
            password=self._configuration.password,
            host=self._configuration.host,
            port=self._configuration.port,
            max_connections=self._configuration.max_connections,
            stale_timeout=self._configuration.stale_timeout,
            autorollback=True
        )
        self._set_utc_timezone(db_inst)

        return db_inst

    def _update_model_databases(self):
        """Updates the database instance for all models."""
        for model in self.models:
            model.set_database(self)

    @staticmethod
    def _set_utc_timezone(db_ins):
        """Sets the timezone of the database connection to UTC."""
        with db_ins.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SET TIME ZONE 'UTC';")
